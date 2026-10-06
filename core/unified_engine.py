"""
OmniDVR Forensic Suite - Unified Multi-Vendor DVR Filesystem Engine
Author: GoatSecurity (GitHub: GoatSecurity)
License: MIT
"""

from typing import List, Tuple, Callable, Optional

from core.disk_io import RawDiskReader
from core.dahua_engine import DahuaEngine, VideoRecording, MAGIC_DHAV, MAGIC_DHFS
from core.hikvision_engine import HikvisionEngine, MAGIC_HIKM, MAGIC_MPEG_PS
from core.generic_cctv import GenericCCTVEngine


class UnifiedDVREngine:
    """
    Intelligent multi-vendor DVR detection and extraction orchestrator.
    Auto-identifies Dahua, Hikvision, and Generic CCTV storage architectures.
    """
    def __init__(self, drive_path: str, sector_size: int = 512):
        self.drive_path = drive_path
        self.sector_size = sector_size
        self.detected_system = "Unknown"

    def detect_system(self) -> str:
        with RawDiskReader(self.drive_path, self.sector_size) as reader:
            # Probe multiple strategic offsets
            for probe_off in [0, 1024*1024, 8*1024*1024, 32*1024*1024, 64*1024*1024, 128*1024*1024, 512*1024*1024]:
                try:
                    chunk = reader.read_chunk(probe_off, 2 * 1024 * 1024)
                except Exception:
                    continue

                if MAGIC_DHAV in chunk or MAGIC_DHFS in chunk:
                    self.detected_system = "Dahua Surveillance (DHFS / DHAV)"
                    return self.detected_system

                if MAGIC_HIKM in chunk or b'HIKVISION' in chunk or MAGIC_MPEG_PS in chunk:
                    self.detected_system = "Hikvision Surveillance (HikFS / PS)"
                    return self.detected_system

        self.detected_system = "Generic CCTV / Raw Stream"
        return self.detected_system

    def scan(self, progress_callback: Optional[Callable[[int, str], None]] = None) -> Tuple[List[VideoRecording], str]:
        system = self.detect_system()

        if "Dahua" in system:
            engine = DahuaEngine(self.drive_path, self.sector_size)
            recordings = engine.scan_timeline(progress_callback=progress_callback)
            return recordings, system

        elif "Hikvision" in system:
            engine = HikvisionEngine(self.drive_path, self.sector_size)
            recordings = engine.scan_timeline(progress_callback=progress_callback)
            return recordings, system

        else:
            engine = GenericCCTVEngine(self.drive_path, self.sector_size)
            recordings = engine.scan_timeline(progress_callback=progress_callback)
            return recordings, system
