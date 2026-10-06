"""
OmniDVR Forensic Suite - About Dialog
Author: GoatSecurity (GitHub: GoatSecurity)
License: MIT
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About OmniDVR Forensic Suite")
        self.resize(520, 390)
        self.setStyleSheet("""
            QDialog {
                background-color: #0b0d13;
                color: #f8fafc;
                border: 1px solid #1a2030;
                border-radius: 12px;
            }
            QLabel { font-size: 13px; color: #94a3b8; }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #00f5ff);
                color: #06090f;
                border: none;
                border-radius: 7px;
                padding: 9px 24px;
                font-weight: 800;
                font-size: 12px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #38bdf8, stop:1 #67e8f9);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(28, 28, 28, 28)

        title = QLabel("🛡️ OmniDVR Forensic Suite v1.0.0")
        title.setStyleSheet("font-size: 20px; font-weight: 900; color: #00f5ff; letter-spacing: 0.5px;")
        layout.addWidget(title)

        author = QLabel("Lead Developer & Architect: <b style='color: #ffffff;'>GoatSecurity</b>")
        layout.addWidget(author)

        badge_free = QLabel("STATUS: 🟢 100% FREE & OPEN-SOURCE (COMMUNITY EDITION)")
        badge_free.setStyleSheet("color: #34d399; font-weight: 800; font-size: 11px; letter-spacing: 0.5px;")
        layout.addWidget(badge_free)

        desc = QLabel(
            "<b>OmniDVR Forensic Suite</b> is an advanced digital forensics workstation tool engineered for "
            "direct physical sector recovery, stream demuxing, and carving of surveillance video storage media.<br><br>"
            "<b>Supported Filesystems & Architectures:</b><br>"
            "• <b>Dahua Technology:</b> DHFS, DHFS4.1, DHFS441, DHAV Raw Stream Demuxer<br>"
            "• <b>Hikvision:</b> HikFS, HIKM, MPEG-PS Camera Transport Streams<br>"
            "• <b>Generic Surveillance:</b> H.264 / H.265 NAL Raw Bitstream Carver (Xiongmai, TVT, Tiandy, Jovision, Uniview)<br><br>"
            "<b>Core Technical Guarantees:</b><br>"
            "• Zero-Crosstalk camera stream isolation (Pure single-channel videos)<br>"
            "• Direct bitstream dumping with zero transcoding delay<br>"
            "• Strict Read-Only low-level physical sector access preserving digital evidentiary integrity."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #64748b; font-size: 12px; line-height: 1.5;")
        layout.addWidget(desc)

        layout.addStretch()

        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_ok = QPushButton("CLOSE")
        btn_ok.clicked.connect(self.close)
        btn_box.addWidget(btn_ok)
        layout.addLayout(btn_box)
