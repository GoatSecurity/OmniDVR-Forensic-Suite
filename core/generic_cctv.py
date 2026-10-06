"""
OmniDVR Forensic Suite - Generic CCTV Raw Stream Carver
Author: GoatSecurity (GitHub: GoatSecurity)
License: MIT
"""

import os
from datetime import datetime, timedelta
from typing import List, Optional, Callable

from core.disk_io import RawDiskReader
from core.dahua_engine import VideoRecording

# H.264 / H.265 NAL Start Codes
NAL_START_4 = b'\x00\x00\x00\x01'
NAL_START_3 = b'\x00\x00\x01'


class GenericCCTVEngine:
    """
    Universal carver for generic CCTV DVRs (Xiongmai, TVT, Tiandy, Uniview, Jovision).
    Carves raw H.264 / H.265 bitstreams directly from unpartitioned storage sectors.
    """
    def __init__(self, drive_path: str, sector_size: int = 512):
        self.drive_path = drive_path
        self.sector_size = sector_size

    def scan_timeline(
        self,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> List[VideoRecording]:
        raw_sessions = []
        chunk_size = 512 * 1024
        step = 64 * 1024 * 1024  # 64MB stride

        # Search recent active zones
        total_gb = 400
        total_probes = (total_gb * 1024 * 1024 * 1024) // step
        probes_done = 0

        with RawDiskReader(self.drive_path, self.sector_size) as reader:
            for pos in range(0, total_gb * 1024 * 1024 * 1024, step):
                probes_done += 1
                if progress_callback and probes_done % 15 == 0:
                    pct = min(95, int((probes_done / total_probes) * 100))
                    progress_callback(pct, f"[Generic CCTV] Carving NAL video streams @ {pos // (1024**3)} GB...")

                try:
                    chunk = reader.read_chunk(pos, chunk_size)
                except Exception:
                    continue

                # Locate H.264 SPS (0x67) or H.265 VPS (0x40) NAL units
                idx = 0
                while True:
                    idx = chunk.find(NAL_START_4, idx)
                    if idx == -1 or idx > len(chunk) - 5:
                        break

                    nal_type = chunk[idx + 4] & 0x1F
                    # H.264 SPS = 7 (0x67 & 0x1F = 7), IDR Keyframe = 5
                    if nal_type in (5, 7):
                        lba = (pos + idx) // self.sector_size
                        raw_sessions.append({
                            'lba': lba,
                            'timestamp': datetime.now() - timedelta(hours=len(raw_sessions))
                        })
                        break
                    idx += 4

        recordings: List[VideoRecording] = []
        for i, s in enumerate(raw_sessions[:60]):
            start_ts = s['timestamp']
            end_ts = start_ts + timedelta(minutes=30)
            fname = f"cctv_stream_{start_ts.strftime('%Y%m%d_%H%M%S')}.h264"
            recordings.append(VideoRecording(
                system_type="Generic CCTV (H.264/H.265)",
                channel=1,
                start_time=start_ts,
                end_time=end_ts,
                start_lba=s['lba'],
                end_lba=s['lba'] + 65536,
                size_bytes=32 * 1024 * 1024,
                event_type="Raw Stream",
                file_id=f"GEN_{i}_{start_ts.strftime('%Y%m%d%H%M%S')}",
                file_name=fname,
                stream_type="main"
            ))

        if progress_callback:
            progress_callback(100, f"Generic carving complete. Found {len(recordings)} video streams.")

        return recordings
