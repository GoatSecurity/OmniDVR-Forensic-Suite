"""
OmniDVR Forensic Suite - Low-Level Physical Disk I/O Module
Author: GoatSecurity (GitHub: GoatSecurity)
License: MIT
"""

import os
import sys
import ctypes
from ctypes import wintypes
import subprocess
from typing import List, Dict, Optional, Tuple

# Win32 Constants
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x00000080
FILE_FLAG_NO_BUFFERING = 0x20000000
FILE_FLAG_RANDOM_ACCESS = 0x10000000

INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value

kernel32 = ctypes.windll.kernel32

CreateFileW = kernel32.CreateFileW
CreateFileW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.LPVOID,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.HANDLE
]
CreateFileW.restype = wintypes.HANDLE

ReadFile = kernel32.ReadFile
ReadFile.argtypes = [
    wintypes.HANDLE,
    wintypes.LPVOID,
    wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD),
    wintypes.LPVOID
]
ReadFile.restype = wintypes.BOOL

CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [wintypes.HANDLE]
CloseHandle.restype = wintypes.BOOL

SetFilePointerEx = kernel32.SetFilePointerEx
SetFilePointerEx.argtypes = [
    wintypes.HANDLE,
    ctypes.c_int64,
    ctypes.POINTER(ctypes.c_int64),
    wintypes.DWORD
]
SetFilePointerEx.restype = wintypes.BOOL

FILE_BEGIN = 0
FILE_CURRENT = 1
FILE_END = 2


def is_admin() -> bool:
    """Checks whether the current process possesses elevated administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def request_admin_elevation():
    """Relaunches the application requesting administrative rights through UAC."""
    if is_admin():
        return True

    script = os.path.abspath(sys.argv[0])
    params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])

    ret = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        f'"{script}" {params}',
        None,
        1
    )
    if ret > 32:
        sys.exit(0)
    return False


def list_physical_drives() -> List[Dict]:
    """
    Enumerate all connected physical storage devices on Windows.
    Provides detailed drive information including model, size, and interface.
    """
    drives = []
    try:
        cmd = 'Get-CimInstance Win32_DiskDrive | Select-Object DeviceID, Index, Model, Size, Partitions, InterfaceType | ConvertTo-Json -Compress'
        proc = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True, timeout=10)
        if proc.returncode == 0 and proc.stdout.strip():
            import json
            data = json.loads(proc.stdout.strip())
            if isinstance(data, dict):
                data = [data]

            for d in data:
                index = d.get('Index', 0)
                size_bytes = int(d.get('Size') or 0)
                size_gb = round(size_bytes / (1024**3), 2)
                size_tb = round(size_bytes / (1024**4), 2)
                size_str = f"{size_tb} TB" if size_tb >= 1.0 else f"{size_gb} GB"
                model = d.get('Model', 'Generic Drive')
                interface = d.get('InterfaceType', 'SATA/USB')

                drives.append({
                    'index': index,
                    'device_id': d.get('DeviceID', f"\\\\.\\PhysicalDrive{index}"),
                    'path': f"\\\\.\\PhysicalDrive{index}",
                    'model': model,
                    'size_bytes': size_bytes,
                    'size_str': size_str,
                    'interface': interface,
                    'partitions': d.get('Partitions', 0),
                    'display_name': f"Disk {index}: {model} [{size_str}] ({interface})"
                })
    except Exception:
        # Fallback raw probing
        for i in range(16):
            path = f"\\\\.\\PhysicalDrive{i}"
            handle = CreateFileW(path, GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE, None, OPEN_EXISTING, 0, None)
            if handle != INVALID_HANDLE_VALUE and handle is not None:
                CloseHandle(handle)
                drives.append({
                    'index': i,
                    'device_id': path,
                    'path': path,
                    'model': f"PhysicalDrive {i}",
                    'size_bytes': 0,
                    'size_str': "Unknown Size",
                    'interface': "Direct",
                    'partitions': 0,
                    'display_name': f"Disk {i}: \\\\.\\PhysicalDrive{i}"
                })
    return drives


class RawDiskReader:
    """
    Forensic raw sector streaming reader.
    Ensures bit-stream integrity, aligned access, and read-only safety.
    """
    def __init__(self, drive_path: str, sector_size: int = 512):
        self.drive_path = drive_path
        self.sector_size = sector_size
        self.handle = INVALID_HANDLE_VALUE
        self._is_open = False

    def open(self) -> bool:
        if self._is_open:
            return True

        self.handle = CreateFileW(
            self.drive_path,
            GENERIC_READ,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            None,
            OPEN_EXISTING,
            FILE_ATTRIBUTE_NORMAL,
            None
        )

        if self.handle == INVALID_HANDLE_VALUE or self.handle is None:
            err = ctypes.GetLastError()
            raise PermissionError(
                f"Failed opening device {self.drive_path} (Win32 Code {err}). "
                "Ensure Administrator privileges are granted and no conflicting application holds an exclusive lock."
            )

        self._is_open = True
        return True

    def close(self):
        if self._is_open and self.handle != INVALID_HANDLE_VALUE:
            CloseHandle(self.handle)
            self.handle = INVALID_HANDLE_VALUE
            self._is_open = False

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def seek_sector(self, sector_lba: int) -> int:
        byte_offset = sector_lba * self.sector_size
        new_pos = ctypes.c_int64(0)
        res = SetFilePointerEx(self.handle, byte_offset, ctypes.byref(new_pos), FILE_BEGIN)
        if not res:
            err = ctypes.GetLastError()
            raise IOError(f"Sector seek failed at LBA {sector_lba} (offset {byte_offset}). Error: {err}")
        return new_pos.value

    def seek_byte(self, byte_offset: int) -> int:
        new_pos = ctypes.c_int64(0)
        res = SetFilePointerEx(self.handle, byte_offset, ctypes.byref(new_pos), FILE_BEGIN)
        if not res:
            err = ctypes.GetLastError()
            raise IOError(f"Byte seek failed at offset {byte_offset}. Error: {err}")
        return new_pos.value

    def read_sectors(self, sector_lba: int, num_sectors: int) -> bytes:
        self.seek_sector(sector_lba)
        bytes_to_read = num_sectors * self.sector_size
        buffer = ctypes.create_string_buffer(bytes_to_read)
        bytes_read = wintypes.DWORD(0)

        success = ReadFile(
            self.handle,
            buffer,
            bytes_to_read,
            ctypes.byref(bytes_read),
            None
        )

        if not success:
            err = ctypes.GetLastError()
            raise IOError(f"Failed reading {num_sectors} sectors at LBA {sector_lba}. Error: {err}")

        return buffer.raw[:bytes_read.value]

    def read_chunk(self, byte_offset: int, size: int) -> bytes:
        aligned_offset = (byte_offset // self.sector_size) * self.sector_size
        offset_diff = byte_offset - aligned_offset
        total_to_read = ((size + offset_diff + self.sector_size - 1) // self.sector_size) * self.sector_size

        self.seek_byte(aligned_offset)
        buffer = ctypes.create_string_buffer(total_to_read)
        bytes_read = wintypes.DWORD(0)

        success = ReadFile(
            self.handle,
            buffer,
            total_to_read,
            ctypes.byref(bytes_read),
            None
        )

        if not success:
            err = ctypes.GetLastError()
            raise IOError(f"Failed reading {total_to_read} bytes at offset {aligned_offset}. Error: {err}")

        data = buffer.raw[:bytes_read.value]
        return data[offset_diff:offset_diff + size]
