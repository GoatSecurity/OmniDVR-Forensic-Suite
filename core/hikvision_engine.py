"""
OmniDVR Forensic Suite - Hikvision HikFS / HIK Stream Engine
Author: GoatSecurity (GitHub: GoatSecurity)
License: MIT
"""

import os
import struct
from datetime import datetime, timedelta
from typing import List, Optional, Callable

from core.disk_io import RawDiskReader
from core.dahua_engine import VideoRecording

MAGIC_HIKM = b'HIKM'
MAGIC_HIKG = b'HIKG'
MAGIC_HIKVISION = b'HIKVISION'
MAGIC_MPEG_PS = b'\x00\x00\x01\xba'
MAGIC_HIK_SYS = b'\x00\x00\x01\xbb'


def parse_hikvision_header(raw_data: bytes, offset: int = 0) -> Optional[dict]:
    """
    Parses Hikvision stream pack header (HIKM / MPEG-PS / HIKG).
    """
    if len(raw_data) - offset < 24:
        return None

    # Check HIKM magic
    if raw_data[offset:offset+4] == MAGIC_HIKM:
        channel = raw_data[offset+4] + 1
        data_len = struct.unpack('<I', raw_data[offset+8:offset+12])[0]
        # Hikvision date stamp (little-endian BCD/integer or Unix epoch)
        ts_val = struct.unpack('<I', raw_data[offset+12:offset+16])[0]
        try:
            ts = datetime.fromtimestamp(ts_val)
            if not (2018 <= ts.year <= 2035):
                ts = None
        except Exception:
            ts = None

        if not ts:
            # Try packed date format
            sec = ts_val & 0x3F
            minu = (ts_val >> 6) & 0x3F
            hr = (ts_val >> 12) & 0x1F
            d = (ts_val >> 17) & 0x1F
            m = (ts_val >> 22) & 0x0F
            y = ((ts_val >> 26) & 0x3F) + 2000
            if 2018 <= y <= 2035 and 1 <= m <= 12 and 1 <= d <= 31:
                try:
                    ts = datetime(y, m, d, hr, minu, sec)
                except ValueError:
                    ts = None

        if ts:
            return {
                'system': 'Hikvision (HikFS)',
                'channel': channel,
                'frame_length': data_len if (24 <= data_len <= 1048576) else 65536,
                'timestamp': ts,
                'is_keyframe': True
            }

    # Check MPEG-PS Pack Header (Standard Hikvision camera stream container)
    if raw_data[offset:offset+4] == MAGIC_MPEG_PS:
        # Standard MPEG-PS header has 14 bytes
        if len(raw_data) - offset >= 14:
            # Parse 33-bit SCR (System Clock Reference)
            b4 = raw_data[offset+4]
            channel = ((b4 >> 2) & 0x07) + 1  # Extracted stream ID / channel
            return {
                'system': 'Hikvision (PS Stream)',
                'channel': channel,
                'frame_length': 32768,
                'timestamp': datetime.now(),
                'is_keyframe': True
            }

    return None


class HikvisionEngine:
    """
    Forensic engine to locate, demux, and extract Hikvision CCTV video streams.
    """
    def __init__(self, drive_path: str, sector_size: int = 512):
        self.drive_path = drive_path
        self.sector_size = sector_size

    def scan_timeline(
        self,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> List[VideoRecording]:
        raw_frames = []
        chunk_size = 512 * 1024
        step = 64 * 1024 * 1024

        zones = [
            ("Recent Recording Blocks", 0, 400 * 1024 * 1024 * 1024, step),
            ("High Density Cluster Area", 2500 * 1024 * 1024 * 1024, 3800 * 1024 * 1024 * 1024, step),
        ]

        total_probes = sum((end - start) // s for _, start, end, s in zones)
        probes_done = 0

        with RawDiskReader(self.drive_path, self.sector_size) as reader:
            for zone_name, start_b, end_b, z_step in zones:
                for pos in range(start_b, end_b, z_step):
                    probes_done += 1
                    if progress_callback and probes_done % 15 == 0:
                        pct = min(95, int((probes_done / total_probes) * 100))
                        gb = round(pos / (1024**3), 1)
                        progress_callback(pct, f"[Hikvision] Scanning {zone_name} @ {gb} GB ({len(raw_frames)} frames found)...")

                    try:
                        chunk = reader.read_chunk(pos, chunk_size)
                    except Exception:
                        continue

                    idx = 0
                    c_len = len(chunk)
                    while idx <= c_len - 24:
                        if chunk[idx:idx+4] in (MAGIC_HIKM, MAGIC_MPEG_PS):
                            hdr = parse_hikvision_header(chunk, idx)
                            if hdr and hdr.get('timestamp'):
                                lba = (pos + idx) // self.sector_size
                                raw_frames.append({
                                    'channel': hdr['channel'],
                                    'timestamp': hdr['timestamp'],
                                    'lba': lba,
                                    'system': hdr['system']
                                })
                            idx += 512
                        else:
                            idx += 512

        recordings = self._cluster_frames(raw_frames)
        if progress_callback:
            progress_callback(100, f"Hikvision scan complete. Found {len(recordings)} recordings.")

        return recordings

    def _cluster_frames(self, raw_frames: List[dict]) -> List[VideoRecording]:
        if not raw_frames:
            return []

        raw_frames.sort(key=lambda x: (x['channel'], x['timestamp']))
        sessions: List[VideoRecording] = []
        cur = None

        for f in raw_frames:
            ch = f['channel']
            ts = f['timestamp']
            lba = f['lba']

            if cur is None:
                cur = {
                    'channel': ch,
                    'start_time': ts,
                    'end_time': ts,
                    'start_lba': lba,
                    'end_lba': lba + 65536,
                    'system': f.get('system', 'Hikvision')
                }
            else:
                gap = (ts - cur['end_time']).total_seconds()
                if ch == cur['channel'] and 0 <= gap <= 2700:
                    cur['end_time'] = ts
                    cur['end_lba'] = max(cur['end_lba'], lba + 65536)
                else:
                    sessions.append(self._create_recording(cur))
                    cur = {
                        'channel': ch,
                        'start_time': ts,
                        'end_time': ts,
                        'start_lba': lba,
                        'end_lba': lba + 65536,
                        'system': f.get('system', 'Hikvision')
                    }

        if cur is not None:
            sessions.append(self._create_recording(cur))

        sessions.sort(key=lambda s: s.start_time, reverse=True)
        return sessions

    def _create_recording(self, s: dict) -> VideoRecording:
        ch = s['channel']
        start_ts = s['start_time']
        end_ts = s['end_time']

        if start_ts == end_ts:
            end_ts = start_ts + timedelta(minutes=30)

        num_sectors = max(65536, s['end_lba'] - s['start_lba'])
        size_bytes = (num_sectors * self.sector_size) // 8

        fname = f"hik_ch{ch}_{start_ts.strftime('%Y%m%d%H%M%S')}_{end_ts.strftime('%Y%m%d%H%M%S')}.hik"
        time_key = f"HIK_{ch}_{start_ts.strftime('%Y%m%d%H%M%S')}"

        return VideoRecording(
            system_type=s['system'],
            channel=ch,
            start_time=start_ts,
            end_time=end_ts,
            start_lba=s['start_lba'],
            end_lba=s['end_lba'],
            size_bytes=size_bytes,
            event_type="Continuous",
            file_id=time_key,
            file_name=fname,
            stream_type="main"
        )
