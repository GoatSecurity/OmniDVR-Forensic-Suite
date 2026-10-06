# 🛡️ OmniDVR Forensic Suite

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg?style=for-the-badge)
![Status](https://img.shields.io/badge/status-100%25%20Free%20%26%20Open%20Source-success.svg?style=for-the-badge)
![Platform](https://img.shields.io/badge/platform-Windows%20x64-0078d7.svg?style=for-the-badge&logo=windows)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-yellow.svg?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)
![Maintained](https://img.shields.io/badge/Author-Goat__Sec-red.svg?style=for-the-badge&logo=github)

**Next-Generation Multi-Vendor CCTV Forensic Stream Demuxer & Sector Carving Suite**

*Designed & Engineered by **[GoatSecurity](https://github.com/GoatSecurity)***

</div>

---

## 📖 Overview

**OmniDVR Forensic Suite** is an advanced, 100% free and open-source digital forensics workstation tool engineered to extract, demultiplex, and carve surveillance video footage directly from raw physical hard drives (`\\.\PhysicalDriveX`).

Unlike conventional generic recovery tools that corrupt CCTV files or mix frames across cameras, **OmniDVR** interfaces directly at the physical sector boundary to provide **zero-crosstalk camera stream isolation**, accurate timestamp parsing, and direct raw bitstream dumps at maximum drive transfer speed.

---

## ⚡ Core Forensic Capabilities

| Feature | Technical Specification |
| :--- | :--- |
| **Multi-Vendor DVR Support** | Seamless detection and extraction for **Dahua** (DHFS, DHFS4.1, DHFS441, DHAV), **Hikvision** (HikFS, HIKM, MPEG-PS), and **Generic Surveillance** (H.264/H.265 NAL carver for Xiongmai, TVT, Tiandy, Uniview, Jovision). |
| **Zero-Crosstalk Demuxing** | Automatically filters interleaved physical sectors by camera channel (1–16). Exported files contain **pure, uninterrupted video from that specific camera alone** with no jumping between camera views. |
| **Direct Bitstream Dump** | Direct passthrough stream dumping (`.dav`, `.hik`, `.h264`) without slow MP4 transcoding delays. Includes automatic SHA-256 evidentiary hash logs. |
| **Timeline Reconstructor** | Auto-sorts recordings strictly from **Newest to Oldest** (including present day `2026-10-05` and active recent footage). |
| **Live Surveillance HUD Preview** | Real-time I-Frame decoding preview dock displaying actual camera snapshots, stream metadata, and integrated player launcher. |
| **100% Free & Unrestricted** | Zero paywalls, zero license keys, zero trial limits. Completely unrestricted open-source forensic software for researchers and investigators. |
| **Forensic Integrity Guard** | Operates strictly in Read-Only mode (`GENERIC_READ` with shared locks) to preserve digital evidentiary integrity. |

---

## 🚀 Quick Start

### Prerequisites
- Windows 10 / 11 (64-bit)
- Python 3.10+
- Administrator privileges (required for Windows physical sector access)
- FFmpeg (optional, recommended for live preview keyframe decoding)

### Installation & Launch
```bash
# 1. Clone the repository
git clone https://github.com/GoatSecurity/OmniDVR-Forensic-Suite.git
cd OmniDVR-Forensic-Suite

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the forensic suite
python main.py
```

---

## 📁 Repository Structure

```text
OmniDVR-Forensic-Suite/
├── core/
│   ├── disk_io.py          # Low-level Win32 aligned sector stream engine
│   ├── dahua_engine.py     # Dahua DHFS/DHAV stream demuxer & timeline parser
│   ├── hikvision_engine.py # Hikvision HikFS & MPEG-PS stream carver
│   ├── generic_cctv.py     # Universal H.264/H.265 NAL bitstream carver
│   ├── unified_engine.py   # Multi-vendor storage auto-detection dispatcher
│   ├── exporter.py         # Direct raw stream bitstream dumper (No MP4 delay)
│   └── preview_worker.py   # Channel-isolated I-frame keyframe snapshot extractor
├── ui/
│   ├── styles.py           # Cyber-forensic dark HUD glassmorphism stylesheet
│   ├── about_dialog.py     # Software information & GoatSecurity attribution
│   └── main_window.py      # Master graphical user interface
├── main.py                 # Application launcher with UAC auto-elevation
├── requirements.txt        # Python dependency manifest
├── LICENSE                 # MIT License (Copyright GoatSecurity)
└── README.md               # Documentation & technical manual
```

---

## ⚖️ License & Attribution

Crafted with passion by **[GoatSecurity](https://github.com/GoatSecurity)**.  
Licensed under the **[MIT License](LICENSE)**. Free for personal, academic, and forensic use.
