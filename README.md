# 🛡️ OmniDVR Forensic Suite

### Open-Source CCTV Video Recovery & DVR/NVR Hard Drive Forensics for Windows

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge" alt="Version 1.0.0">
  <img src="https://img.shields.io/badge/platform-Windows%2010%2F11-0078D7?style=for-the-badge&logo=windows" alt="Windows">
  <img src="https://img.shields.io/badge/python-3.10%2B-yellow?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/open%20source-free-success?style=for-the-badge" alt="Open Source">
</p>

<p align="center">
  <strong>Recover, inspect, and extract supported surveillance video streams from DVR/NVR storage media.</strong>
</p>

<p align="center">
  Developed by <a href="https://github.com/GoatSecurity"><strong>GoatSecurity</strong></a>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-supported-formats">Supported Formats</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-recovery-guide">Recovery Guide</a> •
  <a href="#-faq">FAQ</a>
</p>

---

## 📖 Overview

**OmniDVR Forensic Suite** is an open-source Windows application designed for CCTV video recovery research, DVR/NVR hard drive analysis, surveillance footage extraction, raw video stream carving, and digital video forensics.

Recovering video recordings from a DVR or NVR can be difficult when footage is deleted, inaccessible through the original recorder, stored in a proprietary format, or not visible as ordinary files in Windows.

OmniDVR provides a dedicated workflow for examining physical disk storage, identifying supported video structures, processing compatible recording data, and exporting recoverable video streams.

The project is intended for:

- Digital forensics researchers
- CCTV and security system technicians
- Data recovery specialists
- Incident investigators
- Security professionals
- Developers working with surveillance storage formats
- Users examining DVR/NVR hard drives they own or are authorized to analyze

The actual recovery results depend on the source disk, recorder model, storage format, recording layout, disk condition, and whether the original video data has been overwritten.

> **Important:** OmniDVR does not guarantee recovery of every deleted recording or compatibility with every DVR/NVR model. Test results and verified device compatibility should be evaluated before using recovered material as evidence.

---

## ⚡ Features

### 🔍 Physical Hard Drive Analysis

OmniDVR includes a low-level disk access component designed to examine physical storage devices on Windows.

Example Windows physical disk path:

```text
\\.\PhysicalDrive0
```

Potential use cases include:

- DVR/NVR hard drive examination
- Raw sector inspection
- Surveillance storage analysis
- Investigating disks that Windows cannot interpret as ordinary file volumes
- Searching for supported video data structures

Direct physical disk access requires appropriate permissions and careful identification of the source device.

### 🎥 Multi-Vendor CCTV Video Analysis

The project contains separate processing components intended for supported surveillance storage layouts and video formats.

Targeted format families include:

- Dahua-related storage and video formats
- Hikvision-related storage and video formats
- MPEG Program Stream (MPEG-PS)
- H.264 / AVC elementary streams
- H.265 / HEVC elementary streams
- Compatible raw surveillance video data

Codec support does not automatically guarantee support for every recorder that uses that codec. Proprietary filesystems and recording structures may require additional format-specific handling.

### 🧩 Raw Video Stream Carving

Video stream carving attempts to identify and extract recognizable video data directly from storage.

This can be useful when normal file browsing cannot locate a recording or when examining compatible raw video data.

Recovery results may be incomplete when frames, codec headers, timestamps, audio data, or recording metadata are missing.

### 📹 Camera Channel Separation

Surveillance systems may store recordings from multiple cameras in fragmented or interleaved storage layouts.

OmniDVR includes channel-oriented processing intended to separate supported video data according to available channel information.

The accuracy of channel separation depends on the recorder's storage structure and the correctness of the relevant parser.

### 🕒 Recording Timeline Reconstruction

The project includes timestamp and timeline processing intended to help organize recoverable recordings.

Where reliable timestamp metadata is available, recordings can be arranged for easier examination.

Recovered timestamps should be verified against the original recorder configuration, time zone, and other available evidence.

### 🖥️ Graphical User Interface

OmniDVR provides a Windows-oriented graphical interface for supported analysis and extraction operations.

Depending on the current implementation, the workflow may include disk selection, scan controls, stream information, previews, and export options.

### 📦 Raw Stream Export

The exporter is designed to save extracted data in supported raw or vendor-specific formats.

Potential output extensions include:

- `.h264`
- `.hik`
- `.dav`

The extension used depends on the actual extraction method. Renaming a file does not convert its internal format.

### 🔐 SHA-256 Integrity Hashing

The project includes a SHA-256 hashing workflow for supported exported artifacts.

Hashes can help verify that a file remains unchanged between verification points.

A matching hash does not independently prove that the source recording is authentic, that its timestamps are correct, or that the recovery process was error-free.

### 🆓 Free and Open Source

OmniDVR Forensic Suite is published under the MIT License.

There are no proprietary activation keys required by the MIT license itself. Third-party dependencies remain subject to their own licenses.

---

## 📂 Supported Formats

The following table describes the project's intended compatibility areas. It is not a guarantee that every device or firmware version has been validated.

| Vendor / Format | Intended Analysis Area | Compatibility Notes |
|---|---|---|
| Dahua | Supported DHFS/DHAV-related parsing paths | Depends on the actual storage format and firmware |
| Hikvision | Supported HikFS/HIKM-related parsing paths | Proprietary variants may require additional support |
| MPEG-PS | Program Stream analysis | Requires recognizable stream structures |
| H.264 / AVC | Raw video stream carving | Original timestamps or audio may not be recovered |
| H.265 / HEVC | Raw video stream carving | Valid codec data and headers may be required |
| Other CCTV systems | Compatible raw video data | Codec compatibility does not guarantee filesystem compatibility |

### Compatibility Disclaimer

Device compatibility should be assessed at three separate levels:

1. **Storage recognition:** Can the software recognize the disk layout or recording structure?
2. **Video extraction:** Can it recover valid video stream data?
3. **Playback and interpretation:** Can the extracted data be played and its timestamps and camera attribution verified?

Success at one level does not guarantee success at the others.

For specific device compatibility reports, see the [project repository](https://github.com/GoatSecurity/OmniDVR-Forensic-Suite) and [GitHub Issues](https://github.com/GoatSecurity/OmniDVR-Forensic-Suite/issues).

---

## 🎯 CCTV Video Recovery Use Cases

### Recovering Deleted CCTV Footage

When a recording disappears from a DVR/NVR playback interface, its underlying data may or may not remain on the disk.

Recovery may be possible when the relevant data blocks remain intact and the recording layout can be interpreted. Continued recording can overwrite previous footage and reduce the possibility of successful recovery.

### DVR Hard Drive Recovery

Some DVR systems store video using proprietary layouts that Windows cannot read as ordinary files.

Physical disk analysis may help investigate these storage structures without requiring the disk to appear as a standard Windows volume.

### NVR Video Recovery

NVR storage may contain recordings organized using vendor-specific recording indexes, metadata, or video containers.

The ability to recover those recordings depends on the relevant parser and the condition of the source data.

### CCTV Video Extraction Without the Original Recorder

If the original recorder is unavailable or damaged, a compatible hard drive may still contain recoverable recording data.

Some formats may require the original device, compatible vendor software, or additional metadata to interpret the recordings correctly.

### H.264 and H.265 Video Recovery

Raw stream carving may identify portions of H.264 or H.265 video data on a disk.

Extracted streams may not contain the original recording date, camera identifier, audio, or complete playback information.

### Digital Video Forensics

Extracted recordings and relevant metadata can be documented for further examination.

For potential evidentiary use, preserve the original source, record every acquisition and extraction step, and validate the output using an independently verified workflow.

---

## ⚙️ How It Works

The intended processing workflow is:

1. **Disk Selection** — identify the physical disk or supported source.
2. **Storage Access** — read the source using the applicable disk access implementation.
3. **Format Analysis** — inspect recognizable structures and determine the relevant processing path.
4. **Video Identification** — search for supported recording structures and recognizable video data.
5. **Stream Processing** — extract or separate compatible video data where possible.
6. **Metadata Interpretation** — process available timestamps, channel identifiers, or other supported metadata.
7. **Preview and Export** — inspect results and save supported output artifacts.
8. **Integrity Verification** — calculate SHA-256 hashes where supported.

The precise detection and recovery behavior depends on the current implementation of each processing engine.

---

## 💻 System Requirements

| Component | Requirement |
|---|---|
| Operating System | Windows 10 or Windows 11, 64-bit |
| Python | Python 3.10 or newer, subject to dependency compatibility |
| Permissions | Administrator privileges may be required for physical disk access |
| Storage | Sufficient free space for recovered recordings or disk images |
| FFmpeg | Optional, if required by the installed preview workflow |
| Source | Compatible physical disk, disk image, or supported input |

A separate destination drive is recommended for recovered recordings.

**Never use the source disk as the destination for recovered data.**

---

## 🚀 Installation

### 1. Install Python

Download a compatible 64-bit Python version:

https://www.python.org/downloads/windows/

Verify the installation:

```powershell
py --version
```

### 2. Clone the Repository

```powershell
git clone https://github.com/GoatSecurity/OmniDVR-Forensic-Suite.git

cd OmniDVR-Forensic-Suite
```

### 3. Create a Virtual Environment

```powershell
py -3.11 -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Alternatively, run the virtual environment's Python executable directly without activating it.

### 4. Install Dependencies

```powershell
python -m pip install --upgrade pip

python -m pip install -r requirements.txt
```

If dependency installation fails, check the Python version and the compatibility of the packages listed in `requirements.txt`.

### 5. Launch the Application

If `main.py` is the current application entry point:

```powershell
python main.py
```

Physical disk operations may require Administrator privileges. Before elevated execution, verify the source code, confirm the selected disk, and understand which operations the application performs.

---

## 🧰 Recovery Guide

This workflow is intended for authorized recovery of surveillance footage from a disk you own or are permitted to examine.

### Step 1: Preserve the Source

If the footage may be important, stop using the recorder when safe and practical.

Do not initialize, format, repartition, or repair the original disk before preserving its contents.

### Step 2: Identify the Correct Drive

Verify the disk model, capacity, serial number, and connection method.

Do not assume that `PhysicalDrive0` is the DVR/NVR disk.

### Step 3: Create a Forensic Image

For important data, create a sector-by-sector image with a suitable forensic acquisition tool where possible.

Preserve acquisition logs and verify the image with cryptographic hashes when appropriate.

### Step 4: Analyze a Working Copy

Use a verified working copy or disk image whenever supported.

If the current implementation requires direct physical access, ensure the original source is protected and independently verify the actual access mode.

### Step 5: Scan and Export

Select the relevant analysis method and scan for supported video structures.

Export recovered files to a separate destination drive.

### Step 6: Validate the Results

Check whether the output contains valid video, expected timestamps, and the intended camera channel.

Document incomplete recordings or uncertain metadata rather than treating them as verified evidence.

---

## 🔐 Forensic Integrity and Disk Safety

Digital video recovery can affect evidence if performed incorrectly.

Before examining an important disk, review the implementation of the disk access layer and verify its behavior.

Recommended precautions:

- Preserve the original media whenever possible.
- Prefer forensic imaging and a verified working copy.
- Use a hardware write blocker where appropriate and available.
- Confirm the selected device before starting an operation.
- Save extracted recordings to a separate destination.
- Document acquisition and extraction steps.
- Keep relevant logs and cryptographic hashes.
- Verify whether every component opens the source in read-only mode.
- Validate recovered recordings independently before relying on them.

A read-only access flag or a SHA-256 hash alone is not a guarantee of forensic integrity.

---

## 📦 Output Formats

The export workflow may produce raw or vendor-specific video data.

| Extension | Description |
|---|---|
| `.h264` | May contain an H.264 elementary video stream |
| `.hik` | May contain Hikvision-related or project-specific extracted data |
| `.dav` | May contain Dahua-related or project-specific extracted data |

The actual output format depends on the exporter implementation and source data.

If an exported file cannot be played in a standard media player, it may be incomplete, require additional metadata, use a proprietary container, or need a compatible decoder.

Renaming a file does not change its internal format.

---

## 🛠️ Troubleshooting

### The DVR/NVR Disk Does Not Appear

Check the physical connection, Windows device detection, and required permissions.

If the disk is physically failing, stop repeated scans and consider professional recovery.

### Windows Asks to Format the Disk

Do not format a disk containing recordings you need to recover.

Some surveillance systems use storage structures that Windows cannot interpret as a normal volume. This does not, by itself, prove that the recordings are recoverable or unrecoverable.

### No Video Data Is Found

Possible causes include:

- Unsupported storage layout
- Incompatible recording format
- Overwritten recording data
- Disk read errors
- Incorrect analysis method

Review the logs and, where available, compare the result against a known test sample.

### Exported Video Will Not Play

The stream may be incomplete, missing required headers, contained in a proprietary format, or dependent on a compatible decoder.

Verify the actual output format before attempting any conversion.

### Camera Channels Appear Mixed

Channel separation depends on the parser and the availability of channel metadata.

Treat incorrect channel assignments as a potential parsing issue and report a reproducible example.

### Timestamps Are Incorrect

Check the recorder's clock, configured time zone, timestamp interpretation, and the source of the parsed timestamp.

Do not assume that the computer's current date is the recording date.

### Python Dependencies Fail

Use a compatible Python version, recreate the virtual environment if necessary, and inspect the complete installation error.

When reporting a problem, include the Python version, Windows version, command used, and relevant traceback. Remove sensitive information before publishing logs.

---

## ❓ FAQ

### What is OmniDVR Forensic Suite?

OmniDVR Forensic Suite is an open-source Windows application designed for DVR/NVR hard drive analysis, CCTV video recovery research, surveillance video extraction, and digital video forensics.

### Can OmniDVR recover deleted CCTV footage?

It may recover deleted or inaccessible footage when the relevant data remains on the disk and the source format is supported. Recovery is not guaranteed, especially if the original video has been overwritten.

### Can I recover CCTV footage without the original DVR?

Potentially. A compatible disk may contain recoverable video data even when the recorder is unavailable. Certain proprietary formats may require the original device or additional vendor-specific tools.

### Does it support Dahua DVR/NVR hard drives?

The project targets certain Dahua-related storage and video formats. Compatibility depends on the specific model, firmware, storage layout, and parser implementation.

### Does it support Hikvision DVR/NVR hard drives?

The project targets certain Hikvision-related formats. Support for one format does not guarantee compatibility with every Hikvision recorder.

### Can it recover video from a formatted DVR hard drive?

Recovery may be possible if the relevant data remains intact and the storage layout can be interpreted. New recordings or other writes may overwrite the original footage.

### Does it support H.264 and H.265?

The project includes carving paths intended for compatible H.264/H.265 data. Extracting a valid stream does not necessarily restore the original container, audio, timestamps, or camera metadata.

### Is OmniDVR free?

The project is distributed under the MIT License. Review the repository's license and the licenses of its third-party dependencies.

### Does it support every CCTV brand?

No universal compatibility guarantee is made. Support depends on the actual recording format, storage layout, and relevant parser implementation.

### Is recovered footage automatically court-ready?

No. Evidentiary use requires appropriate acquisition procedures, documented handling, integrity verification, and validation of the recovery method.

### Where can I report a bug?

Report bugs and request features through the official issue tracker:

https://github.com/GoatSecurity/OmniDVR-Forensic-Suite/issues

For compatibility issues, include the recorder model, firmware where known, storage information, relevant logs, and reproducible details.

Do not publish private surveillance footage, credentials, or sensitive evidence.

---

## 🗂️ Project Structure

The intended module layout is shown below. Verify that the filenames match the current repository before relying on this list.

```text
OmniDVR-Forensic-Suite/
├── core/
│   ├── disk_io.py
│   ├── dahua_engine.py
│   ├── hikvision_engine.py
│   ├── generic_cctv.py
│   ├── unified_engine.py
│   ├── exporter.py
│   └── preview_worker.py
├── ui/
│   ├── styles.py
│   ├── about_dialog.py
│   └── main_window.py
├── main.py
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🤝 Contributing

Contributions are welcome from developers, digital forensics researchers, CCTV technicians, and data recovery specialists.

Useful contributions include:

- Reproducible bug reports
- Verified device compatibility reports
- Storage format documentation
- Improvements to stream parsing and timestamp interpretation
- Tests for channel separation and timeline reconstruction
- Performance improvements that preserve data integrity
- Legally obtained test fixtures that do not expose private surveillance footage

Before submitting a pull request:

1. Describe the problem and proposed change.
2. Include a reproducible test case where possible.
3. Document assumptions about the relevant storage format.
4. Avoid sharing private footage, credentials, or sensitive forensic evidence.
5. Describe any impact on disk access or forensic integrity.

Use the official [GitHub Issues](https://github.com/GoatSecurity/OmniDVR-Forensic-Suite/issues) page for bug reports and feature requests.

---

## 🛡️ Security and Responsible Use

OmniDVR is intended for lawful data recovery, authorized security research, and legitimate digital forensic work.

Only examine storage devices that you own or are explicitly authorized to access.

Do not use recovered surveillance footage to violate privacy, bypass lawful access restrictions, or distribute confidential recordings without authorization.

Report security vulnerabilities responsibly to the project maintainer.

---

## 📄 License

OmniDVR Forensic Suite is distributed under the [MIT License](LICENSE).

See the `LICENSE` file for the applicable terms.

The software is provided "as is", without warranty of any kind, to the extent permitted by applicable law.

---

## 👨‍💻 Author

**GoatSecurity**

- GitHub Organization: https://github.com/GoatSecurity
- Project Repository: https://github.com/GoatSecurity/OmniDVR-Forensic-Suite
- Issues and Feature Requests: https://github.com/GoatSecurity/OmniDVR-Forensic-Suite/issues

---

<p align="center">
  <strong>OmniDVR Forensic Suite</strong><br>
  Open-source tools for CCTV storage analysis, DVR/NVR hard drive examination, and surveillance video recovery research.
</p>
