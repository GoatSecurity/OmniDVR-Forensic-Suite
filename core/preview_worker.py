"""
OmniDVR Forensic Suite - Live Camera Preview & Frame Decoupler
Author: GoatSecurity (GitHub: GoatSecurity)
License: MIT
"""

import os
import subprocess
import tempfile
from typing import Optional

from core.disk_io import RawDiskReader
from core.dahua_engine import parse_dhav_header, MAGIC_DHAV


def extract_keyframe_image(raw_chunk: bytes, target_channel: int = 1) -> Optional[bytes]:
    """
    Decodes an I-Frame image corresponding to target_channel.
    Uses FFmpeg or OpenCV to render a high-clarity JPEG frame.
    """
    if not raw_chunk or len(raw_chunk) < 2048:
        return None

    # Filter for target channel if DHAV stream
    idx = 0
    buf_len = len(raw_chunk)
    target_frames = b''

    while idx <= buf_len - 24:
        if raw_chunk[idx:idx+4] == MAGIC_DHAV:
            hdr = parse_dhav_header(raw_chunk, idx)
            if hdr:
                frame_len = hdr['frame_length']
                if 24 <= frame_len <= 1048576 and idx + frame_len <= buf_len:
                    if hdr['channel'] == target_channel:
                        target_frames += raw_chunk[idx:idx+frame_len]
                        if len(target_frames) > 300 * 1024:
                            break
                    idx += frame_len
                    continue
            idx += 4
        else:
            idx += 4

    payload = target_frames if target_frames else raw_chunk

    # Decode via FFmpeg pipe
    try:
        cmd = [
            'ffmpeg', '-y',
            '-err_detect', 'ignore_err',
            '-i', 'pipe:0',
            '-vframes', '1',
            '-f', 'image2',
            '-vcodec', 'mjpeg',
            'pipe:1'
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        jpeg_data, _ = proc.communicate(input=payload, timeout=5)
        if proc.returncode == 0 and jpeg_data and len(jpeg_data) > 500:
            return jpeg_data
    except Exception:
        pass

    # Disk temp fallback
    try:
        with tempfile.NamedTemporaryFile(suffix='.raw', delete=False) as tmp:
            tmp.write(payload)
            tmp_path = tmp.name

        out_jpg = tmp_path + '.jpg'
        cmd2 = [
            'ffmpeg', '-y',
            '-err_detect', 'ignore_err',
            '-i', tmp_path,
            '-vframes', '1',
            '-q:v', '2',
            out_jpg
        ]
        subprocess.run(cmd2, capture_output=True, timeout=5)
        if os.path.exists(out_jpg) and os.path.getsize(out_jpg) > 500:
            with open(out_jpg, 'rb') as f:
                data = f.read()
            os.remove(out_jpg)
            os.remove(tmp_path)
            return data
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
    except Exception:
        pass

    return None
