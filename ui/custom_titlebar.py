"""
OmniDVR Forensic Suite - Custom Cyber-Forensic Titlebar
Provides custom draggable window chrome with minimize, maximize/restore, and close buttons.
Author: GoatSecurity (GitHub: GoatSecurity)
License: MIT
"""

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton


class CustomTitleBar(QFrame):
    """
    Modern custom window titlebar with integrated dragging and controls.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.setObjectName("customTitleBar")
        self._drag_start_pos: QPoint = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 4, 10, 4)
        layout.setSpacing(10)

        # Brand Icon & Title
        lbl_icon = QLabel("🛡️")
        lbl_icon.setStyleSheet("font-size: 14px;")
        layout.addWidget(lbl_icon)

        self.lbl_title = QLabel("OMNIDVR FORENSIC SUITE")
        self.lbl_title.setObjectName("titleAppText")
        layout.addWidget(self.lbl_title)

        lbl_badge = QLabel("GOATSECURITY")
        lbl_badge.setObjectName("titleGoatBadge")
        layout.addWidget(lbl_badge)

        layout.addStretch()

        # Window Control Buttons
        self.btn_min = QPushButton("―")
        self.btn_min.setObjectName("winMinBtn")
        self.btn_min.setToolTip("Minimize")
        self.btn_min.clicked.connect(self.parent_window.showMinimized)
        layout.addWidget(self.btn_min)

        self.btn_max = QPushButton("◻")
        self.btn_max.setObjectName("winMaxBtn")
        self.btn_max.setToolTip("Maximize / Restore")
        self.btn_max.clicked.connect(self.toggle_maximize)
        layout.addWidget(self.btn_max)

        self.btn_close = QPushButton("✕")
        self.btn_close.setObjectName("winCloseBtn")
        self.btn_close.setToolTip("Close Application")
        self.btn_close.clicked.connect(self.parent_window.close)
        layout.addWidget(self.btn_close)

    def toggle_maximize(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
            self.btn_max.setText("◻")
        else:
            self.parent_window.showMaximized()
            self.btn_max.setText("❐")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_start_pos is not None:
            if not self.parent_window.isMaximized():
                self.parent_window.move(event.globalPosition().toPoint() - self._drag_start_pos)
                event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_start_pos = None
        event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_maximize()
            event.accept()
