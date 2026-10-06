"""
OmniDVR Forensic Suite - Dahua DHFS / DHAV Stream Engine
Author: GoatSecurity (GitHub: GoatSecurity)
License: MIT
"""

import os
import struct
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Callable

from core.disk_io import RawDiskReader

MAGIC_DHFS = b'DHFS'
MAGIC_DHFS441 = b'DHFS441'
MAGIC_DHAV = b'DHAV'
MAGIC_FOOTER = b'dhav'


@dataclass
class VideoRecording:
    """Represents a clean, single-channel CCTV recording session."""
    system_type: str                  # 'Dahua (DHAV)', 'Hikvision (HikFS)', 'Generic CCTV'
    channel: int                      # 1-indexed (Camera 1..16)
    start_time: datetime              # Timestamp of first keyframe
    end_time: datetime                # Timestamp of last frame
    start_lba: int                    # Sector LBA offset
    end_lba: int                      # Ending LBA
    size_bytes: int                   # Calculated stream size
    event_type: str                   # 'Continuous', 'Motion', 'Alarm'
    file_id: str                      # Unique identifier
    file_name: str                    # Standardized export filename
    stream_type: str = 'main'         # 'main' or 'sub'

    @property
    def duration_seconds(self) -> int:
        delta = (self.end_time - self.start_time).total_seconds()
        return max(0, int(delta))

    @property
    def duration_str(self) -> str:
        s = self.duration_seconds
        h = s // 3600
        m = (s % 3600) // 60
        sec = s % 60
        return f"{h:02d}:{m:02d}:{sec:02d}"

    @property
    def size_mb(self) -> float:
        return round(self.size_bytes / (1024 * 1024), 2)


def parse_dhav_date(date_val: int) -> Optional[datetime]:
    """
    Decodes the 32-bit packed integer date found in DHAV headers.
    Exact FFmpeg libavformat/dhav.c get_timeinfo algorithm:
    second = date & 0x3F;
    minute = (date >> 6) & 0x3F;
    hour   = (date >> 12) & 0x1F;
    day    = (date >> 17) & 0x1F;
    month  = (date >> 22) & 0x0F;
    year   = ((date >> 26) & 0x3F) + 2000;
    """
    if date_val == 0 or date_val == 0xFFFFFFFF:
        return None

    sec = date_val & 0x3F
    minu = (date_val >> 6) & 0x3F
    hr = (date_val >> 12) & 0x1F
    d = (date_val >> 17) & 0x1F
    m = (date_val >> 22) & 0x0F
    y = ((date_val >> 26) & 0x3F) + 2000

    if 2018 <= y <= 2035 and 1 <= m <= 12 and 1 <= d <= 31 and 0 <= hr <= 23 and 0 <= minu <= 59 and 0 <= sec <= 59:
        try:
            return datetime(y, m, d, hr, minu, sec)
        except ValueError:
            return None
    return None


def parse_dhav_header(raw_data: bytes, offset: int = 0) -> Optional[dict]:
    """
    Parses a 24-byte DHAV frame header.
    Offset 0..3:   'DHAV' (4 bytes)
    Offset 4:      type (0xfc=video, 0xfd=audio)
    Offset 5:      subtype
    Offset 6:      channel (0-indexed, 0=Ch1, 7=Ch8)
    Offset 7:      frame_subnumber
    Offset 8..11:  frame_number (uint32 LE)
    Offset 12..15: frame_length (uint32 LE)
    Offset 16..19: date (uint32 LE packed)
    Offset 20..23: timestamp/pts
    """
    if len(raw_data) - offset < 24:
        return None

    if raw_data[offset:offset+4] != MAGIC_DHAV:
        return None

    frame_type = raw_data[offset + 4]
    raw_ch = raw_data[offset + 6]
    channel = raw_ch + 1  # Standard 1-based camera ID

    frame_length = struct.unpack('<I', raw_data[offset+12:offset+16])[0]
    date_val = struct.unpack('<I', raw_data[offset+16:offset+20])[0]

    ts = parse_dhav_date(date_val)
    if not ts:
        return None

    is_keyframe = (frame_type in (0xFC, 0x80, 0x00))

    return {
        'magic': 'DHAV',
        'channel': channel,
        'frame_type': frame_type,
        'is_keyframe': is_keyframe,
        'frame_length': frame_length,
        'timestamp': ts,
        'offset': offset
    }


class DahuaEngine:
    """
    High-speed multi-zone scanner and session reconstructor for Dahua DVR drives.
    """
    def __init__(self, drive_path: str, sector_size: int = 512):
        self.drive_path = drive_path
        self.sector_size = sector_size

    def scan_timeline(
        self,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> List[VideoRecording]:
        raw_frames = []
        chunk_size = 512 * 1024  # 512KB probe block
        step = 32 * 1024 * 1024  # 32MB stride

        # Strategic timeline zones across standard DVR platter layouts:
        # Zone 1: Current wrap-around ring-buffer (Today / Newest files)
        # Zone 2: Pre-wrap active recording zone
        # Zone 3: Full archive grid
        zones = [
            ("Active Ring Buffer (Newest)", 0, 500 * 1024 * 1024 * 1024, step),
            ("High Density Zone (August/Recent)", 2800 * 1024 * 1024 * 1024, 3800 * 1024 * 1024 * 1024, step),
            ("Deep Archive Timeline", 500 * 1024 * 1024 * 1024, 2800 * 1024 * 1024 * 1024, step * 4)
        ]

        total_probes = sum((end - start) // s for _, start, end, s in zones)
        probes_done = 0

        with RawDiskReader(self.drive_path, self.sector_size) as reader:
            for zone_name, start_b, end_b, z_step in zones:
                for pos in range(start_b, end_b, z_step):
                    probes_done += 1
                    if progress_callback and probes_done % 20 == 0:
                        pct = min(95, int((probes_done / total_probes) * 100))
                        gb = round(pos / (1024**3), 1)
                        progress_callback(pct, f"[Dahua] Probing {zone_name} @ {gb} GB ({len(raw_frames)} frames captured)...")

                    try:
                        chunk = reader.read_chunk(pos, chunk_size)
                    except Exception:
                        continue

                    idx = 0
                    c_len = len(chunk)
                    while idx <= c_len - 24:
                        if chunk[idx:idx+4] == MAGIC_DHAV:
                            hdr = parse_dhav_header(chunk, idx)
                            if hdr and hdr.get('timestamp'):
                                lba = (pos + idx) // self.sector_size
                                raw_frames.append({
                                    'channel': hdr['channel'],
                                    'timestamp': hdr['timestamp'],
                                    'lba': lba,
                                    'is_keyframe': hdr['is_keyframe']
                                })
                            idx += 4
                        else:
                            idx += 4

        if progress_callback:
            progress_callback(96, "Demuxing single-camera streams and sorting chronologically...")

        recordings = self._cluster_frames(raw_frames)
        if progress_callback:
            progress_callback(100, f"Dahua scan complete. Found {len(recordings)} single-camera recordings.")

        return recordings

    def _cluster_frames(self, raw_frames: List[dict]) -> List[VideoRecording]:
        if not raw_frames:
            return []

        # Sort strictly by camera channel, then timestamp
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
                    'end_lba': lba + 65536
                }
            else:
                gap = (ts - cur['end_time']).total_seconds()
                # Group consecutive frames of the same channel (gap <= 45 mins)
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
                        'end_lba': lba + 65536
                    }

        if cur is not None:
            sessions.append(self._create_recording(cur))

        # Sort all sessions: NEWEST TO OLDEST
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

        fname = f"ch{ch}_main_{start_ts.strftime('%Y%m%d%H%M%S')}_{end_ts.strftime('%Y%m%d%H%M%S')}.dav"
        time_key = f"DHAV_{ch}_{start_ts.strftime('%Y%m%d%H%M%S')}"

        return VideoRecording(
            system_type="Dahua (DHAV)",
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
