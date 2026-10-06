"""
OmniDVR Forensic Suite - Direct Raw Stream Exporter (No MP4 Conversion)
Author: GoatSecurity (GitHub: GoatSecurity)
License: MIT
"""

import os
import hashlib
from typing import Callable, Optional

from core.disk_io import RawDiskReader
from core.dahua_engine import VideoRecording, parse_dhav_header, MAGIC_DHAV


class DirectStreamExporter:
    """
    Forensic raw stream exporter.
    Directly extracts bit-for-bit video streams to disk with zero conversion overhead,
    ensuring maximum I/O transfer throughput and absolute evidentiary integrity.
    """
    def __init__(self, drive_path: str, sector_size: int = 512):
        self.drive_path = drive_path
        self.sector_size = sector_size
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def export_recording(
        self,
        recording: VideoRecording,
        output_dir: str,
        progress_cb: Optional[Callable[[int, str], None]] = None
    ) -> str:
        """
        Extracts the recording directly to output_dir without any transcoding.
        For Dahua streams, performs stream demuxing to guarantee a 100% pure single-camera file.
        """
        os.makedirs(output_dir, exist_ok=True)
        raw_output_path = os.path.join(output_dir, recording.file_name)

        target_channel = recording.channel
        num_sectors = max(2048, recording.end_lba - recording.start_lba)
        chunk_sectors = 4096  # 2MB sector block reads for maximum NVMe/SATA throughput

        bytes_written = 0
        hasher = hashlib.sha256()

        with RawDiskReader(self.drive_path, self.sector_size) as reader:
            with open(raw_output_path, 'wb') as out_f:
                sectors_read = 0
                buffer = b''

                is_dahua = "Dahua" in recording.system_type

                while sectors_read < num_sectors and not self._is_cancelled:
                    batch = min(chunk_sectors, num_sectors - sectors_read)
                    current_lba = recording.start_lba + sectors_read

                    try:
                        chunk = reader.read_sectors(current_lba, batch)
                        if not chunk:
                            break
                        sectors_read += batch
                    except Exception:
                        break

                    if is_dahua:
                        # Demux and only keep target camera packets
                        buffer += chunk
                        idx = 0
                        buf_len = len(buffer)
                        while idx <= buf_len - 24:
                            if buffer[idx:idx+4] == MAGIC_DHAV:
                                hdr = parse_dhav_header(buffer, idx)
                                if hdr:
                                    frame_len = hdr['frame_length']
                                    if frame_len < 24 or frame_len > 2 * 1024 * 1024:
                                        idx += 4
                                        continue

                                    if idx + frame_len <= buf_len:
                                        if hdr['channel'] == target_channel:
                                            frame_bytes = buffer[idx:idx+frame_len]
                                            out_f.write(frame_bytes)
                                            hasher.update(frame_bytes)
                                            bytes_written += len(frame_bytes)
                                        idx += frame_len
                                        continue
                                    else:
                                        break
                                else:
                                    idx += 4
                            else:
                                idx += 4

                        buffer = buffer[idx:]
                    else:
                        # Direct raw stream write for Hikvision or Generic
                        out_f.write(chunk)
                        hasher.update(chunk)
                        bytes_written += len(chunk)

                    if progress_cb:
                        pct = int((sectors_read / num_sectors) * 100)
                        mb = bytes_written // (1024 * 1024)
                        progress_cb(pct, f"Direct Dump: {mb} MB written ({pct}%)")

        if self._is_cancelled or bytes_written == 0:
            if os.path.exists(raw_output_path):
                os.remove(raw_output_path)
            return ""

        # Write forensic SHA-256 hash log alongside the exported file
        hash_file = raw_output_path + ".sha256"
        try:
            with open(hash_file, "w") as hf:
                hf.write(f"{hasher.hexdigest()} *{os.path.basename(raw_output_path)}\n")
        except Exception:
            pass

        return raw_output_path
