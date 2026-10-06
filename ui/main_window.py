"""
OmniDVR Forensic Suite - Master Cyber-Forensic Graphical Interface
Author: GoatSecurity (GitHub: GoatSecurity)
License: MIT
"""

import os
import sys
import tempfile
from datetime import datetime
from typing import List, Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QComboBox, QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
    QProgressBar, QFileDialog, QMessageBox, QStatusBar, QFrame,
    QTextEdit
)
from PyQt6.QtGui import QIcon, QFont, QColor, QPixmap, QImage, QPainter, QPen, QBrush

from core.disk_io import list_physical_drives, RawDiskReader
from core.dahua_engine import VideoRecording
from core.unified_engine import UnifiedDVREngine
from core.exporter import DirectStreamExporter
from core.preview_worker import extract_keyframe_image

from ui.styles import FORENSIC_THEME
from ui.custom_titlebar import CustomTitleBar
from ui.about_dialog import AboutDialog


class ScanWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list, str)
    failed = pyqtSignal(str)

    def __init__(self, drive_path: str):
        super().__init__()
        self.drive_path = drive_path

    def run(self):
        try:
            engine = UnifiedDVREngine(self.drive_path)
            recordings, sys_name = engine.scan(progress_callback=self.progress.emit)
            self.finished.emit(recordings, sys_name)
        except Exception as e:
            import traceback
            self.failed.emit(f"{str(e)}\n\n{traceback.format_exc()}")


class PreviewWorker(QThread):
    frame_ready = pyqtSignal(bytes, str)

    def __init__(self, drive_path: str, start_lba: int, target_channel: int, file_id: str):
        super().__init__()
        self.drive_path = drive_path
        self.start_lba = start_lba
        self.target_channel = target_channel
        self.file_id = file_id

    def run(self):
        try:
            with RawDiskReader(self.drive_path) as reader:
                chunk = reader.read_sectors(self.start_lba, 8192)
                img_data = extract_keyframe_image(chunk, self.target_channel)
                if img_data:
                    self.frame_ready.emit(img_data, self.file_id)
        except Exception:
            pass


class ExportWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(int)

    def __init__(self, drive_path: str, recordings: List[VideoRecording], out_dir: str):
        super().__init__()
        self.drive_path = drive_path
        self.recordings = recordings
        self.out_dir = out_dir
        self.exporter = DirectStreamExporter(self.drive_path)

    def run(self):
        total = len(self.recordings)
        saved = 0
        for idx, rec in enumerate(self.recordings):
            def cb(pct, msg):
                overall = int(((idx + (pct / 100)) / total) * 100)
                self.progress.emit(overall, f"Dumping [{idx+1}/{total}] {rec.file_name}: {msg}")

            res = self.exporter.export_recording(rec, self.out_dir, progress_cb=cb)
            if res:
                saved += 1
        self.finished.emit(saved)


class OmniDVRMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Frameless modern cyber window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        # Comfortable window dimensions (Not full-screen on launch)
        self.resize(1380, 840)
        self.center_on_screen()
        self.setStyleSheet(FORENSIC_THEME)

        self.all_recordings: List[VideoRecording] = []
        self.displayed_recordings: List[VideoRecording] = []
        self.selected_recording: Optional[VideoRecording] = None
        self.detected_system: str = "Awaiting Disk Scan"

        self.setup_ui()
        self.refresh_drives()

    def center_on_screen(self):
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            x = (geo.width() - self.width()) // 2
            y = (geo.height() - self.height()) // 2
            self.move(max(0, x), max(0, y))

    def setup_ui(self):
        main_container = QWidget()
        self.setCentralWidget(main_container)
        root_layout = QVBoxLayout(main_container)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Custom Draggable Title Bar with Controls
        self.title_bar = CustomTitleBar(self)
        root_layout.addWidget(self.title_bar)

        # 2. Command Navigation Bar
        nav_bar = QFrame()
        nav_bar.setObjectName("topNav")
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(14, 8, 14, 8)
        nav_layout.setSpacing(10)

        # Storage Drive Selector
        lbl_drive = QLabel("STORAGE DRIVE:")
        lbl_drive.setObjectName("navLabel")
        nav_layout.addWidget(lbl_drive)

        self.drive_combo = QComboBox()
        nav_layout.addWidget(self.drive_combo)

        btn_refresh = QPushButton("🔄 Refresh")
        btn_refresh.setToolTip("Re-scan physical disk interfaces")
        btn_refresh.clicked.connect(self.refresh_drives)
        nav_layout.addWidget(btn_refresh)

        # Scan Action Button
        self.btn_scan = QPushButton("⚡ SCAN DRIVE")
        self.btn_scan.setObjectName("btnScan")
        self.btn_scan.setToolTip("Start multi-vendor forensic scan")
        self.btn_scan.clicked.connect(self.start_scan)
        nav_layout.addWidget(self.btn_scan)

        # Detected System Badge
        self.lbl_sys_badge = QLabel("SYSTEM: READY")
        self.lbl_sys_badge.setObjectName("sysBadge")
        nav_layout.addWidget(self.lbl_sys_badge)

        # Camera Filter
        lbl_cam = QLabel("CAMERA:")
        lbl_cam.setObjectName("navLabel")
        nav_layout.addWidget(lbl_cam)

        self.cam_combo = QComboBox()
        self.cam_combo.addItem("All Channels (1–16)", 0)
        for i in range(1, 17):
            self.cam_combo.addItem(f"Channel {i:02d}", i)
        self.cam_combo.currentIndexChanged.connect(self.apply_filters)
        nav_layout.addWidget(self.cam_combo)

        # Search Bar
        self.search_box = QLineEdit()
        self.search_box.setObjectName("searchBox")
        self.search_box.setPlaceholderText("🔍 Filter (20261005, 20260823, ch8)...")
        self.search_box.textChanged.connect(self.apply_filters)
        nav_layout.addWidget(self.search_box)

        nav_layout.addStretch()

        # About Dialog Button
        btn_about = QPushButton("ℹ️ About")
        btn_about.clicked.connect(lambda: AboutDialog(self).exec())
        nav_layout.addWidget(btn_about)

        # Direct Export Action
        self.btn_export = QPushButton("💾 DIRECT RAW DUMP")
        self.btn_export.setObjectName("btnExport")
        self.btn_export.setToolTip("Dump pure raw bitstream files without MP4 conversion")
        self.btn_export.clicked.connect(self.export_selected)
        nav_layout.addWidget(self.btn_export)

        root_layout.addWidget(nav_bar)

        # 3. Telemetry Ribbon (Quick Intelligence Stats)
        telemetry = QFrame()
        telemetry.setObjectName("telemetryBar")
        t_layout = QHBoxLayout(telemetry)
        t_layout.setContentsMargins(16, 5, 16, 5)
        t_layout.setSpacing(10)

        self.chip_count = QLabel("📊 Total Streams: 0")
        self.chip_count.setObjectName("chipLabel")
        t_layout.addWidget(self.chip_count)

        self.chip_size = QLabel("💾 Total Capacity: 0.0 GB")
        self.chip_size.setObjectName("chipLabel")
        t_layout.addWidget(self.chip_size)

        self.chip_channels = QLabel("📹 Active Cameras: 0 Channels")
        self.chip_channels.setObjectName("chipLabel")
        t_layout.addWidget(self.chip_channels)

        self.chip_range = QLabel("⏱️ Timeline: Awaiting Scan")
        self.chip_range.setObjectName("chipLabel")
        t_layout.addWidget(self.chip_range)

        t_layout.addStretch()

        lbl_edition = QLabel("🟢 100% Free & Open-Source (GoatSecurity)")
        lbl_edition.setStyleSheet("color: #34d399; font-weight: 800; font-size: 11px;")
        t_layout.addWidget(lbl_edition)

        root_layout.addWidget(telemetry)

        # 4. Center Workspace Splitter: Table (68%) vs Live Monitor Dock (32%)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setContentsMargins(14, 12, 14, 12)
        splitter.setChildrenCollapsible(False)

        # Left Container: Recording Table
        left_box = QWidget()
        left_layout = QVBoxLayout(left_box)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        table_header = QHBoxLayout()
        self.lbl_table_title = QLabel("SURVEILLANCE STREAM INDEX — CHRONOLOGICAL (NEWEST TO OLDEST)")
        self.lbl_table_title.setStyleSheet("font-size: 11px; font-weight: 800; color: #00f5ff; letter-spacing: 0.8px;")
        table_header.addWidget(self.lbl_table_title)
        table_header.addStretch()

        btn_select_toggle = QPushButton("Select / Deselect All")
        btn_select_toggle.clicked.connect(self.toggle_select_all)
        table_header.addWidget(btn_select_toggle)
        left_layout.addLayout(table_header)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(9)
        self.table_widget.setHorizontalHeaderLabels([
            "Select", "System", "File Name", "Channel", "Start Timestamp", "End Timestamp", "Duration", "Size (MB)", "Sector LBA"
        ])
        self.table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.itemSelectionChanged.connect(self.on_row_selected)
        left_layout.addWidget(self.table_widget)

        splitter.addWidget(left_box)

        # Right Container: High-Tech Live Surveillance Monitor Dock
        right_panel = QFrame()
        right_panel.setObjectName("previewCard")
        right_panel.setMinimumWidth(390)
        right_panel.setMaximumWidth(480)
        preview_layout = QVBoxLayout(right_panel)
        preview_layout.setSpacing(12)

        prev_header = QHBoxLayout()
        lbl_prev_title = QLabel("LIVE CAMERA HUD PREVIEW")
        lbl_prev_title.setStyleSheet("font-size: 12px; font-weight: 800; color: #00f5ff; letter-spacing: 0.8px;")
        prev_header.addWidget(lbl_prev_title)
        prev_header.addStretch()

        self.lbl_rec_indicator = QLabel("REC ● STANDBY")
        self.lbl_rec_indicator.setStyleSheet("color: #10b981; font-weight: 800; font-size: 10px; letter-spacing: 0.5px;")
        prev_header.addWidget(self.lbl_rec_indicator)
        preview_layout.addLayout(prev_header)

        # Camera Snapshot Display
        self.lbl_preview_screen = QLabel()
        self.lbl_preview_screen.setObjectName("previewScreen")
        self.lbl_preview_screen.setFixedHeight(250)
        self.lbl_preview_screen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_preview_screen.setText("┌                                              ┐\n\nSELECT RECORDING TO DECODE KEYFRAME\n\n└                                              ┘")
        self.lbl_preview_screen.setStyleSheet("color: #334155; font-size: 11px; font-weight: 700; font-family: monospace;")
        preview_layout.addWidget(self.lbl_preview_screen)

        # Telemetry Metadata Box
        self.info_box = QTextEdit()
        self.info_box.setObjectName("hudInfoBox")
        self.info_box.setReadOnly(True)
        self.info_box.setFixedHeight(190)
        self.info_box.setHtml("<span style='color: #475569;'>Awaiting recording selection. Click any row to inspect stream descriptors.</span>")
        preview_layout.addWidget(self.info_box)

        # Action Buttons
        act_box = QHBoxLayout()
        self.btn_play_clip = QPushButton("▶ LAUNCH PLAYER")
        self.btn_play_clip.setObjectName("btnPlay")
        self.btn_play_clip.clicked.connect(self.play_selected_clip)
        act_box.addWidget(self.btn_play_clip)

        self.btn_save_single = QPushButton("💾 DUMP STREAM")
        self.btn_save_single.setObjectName("btnExport")
        self.btn_save_single.clicked.connect(self.save_single_recording)
        act_box.addWidget(self.btn_save_single)

        preview_layout.addLayout(act_box)
        preview_layout.addStretch()

        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        root_layout.addWidget(splitter)

        # 5. Bottom Progress & Status Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        root_layout.addWidget(self.progress_bar)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Select storage drive and click 'SCAN DRIVE' to begin forensic extraction.")

    def refresh_drives(self):
        self.drive_combo.clear()
        drives = list_physical_drives()
        dahua_idx = 0
        for i, d in enumerate(drives):
            text = f"{d['display_name']}"
            self.drive_combo.addItem(text, d['path'])
            if "JMicron" in d['model'] or d['index'] == 2 or d['size_bytes'] > 3000000000000:
                dahua_idx = i
        if self.drive_combo.count() > 0:
            self.drive_combo.setCurrentIndex(dahua_idx)

    def start_scan(self):
        drive_path = self.drive_combo.currentData()
        if not drive_path:
            QMessageBox.warning(self, "Warning", "Please select a target physical drive.")
            return

        self.btn_scan.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setValue(5)
        self.status_bar.showMessage("Analyzing disk signatures and partition tables...")

        self.worker = ScanWorker(drive_path)
        self.worker.progress.connect(self.on_scan_progress)
        self.worker.finished.connect(self.on_scan_finished)
        self.worker.failed.connect(self.on_scan_failed)
        self.worker.start()

    def on_scan_progress(self, pct: int, msg: str):
        self.progress_bar.setValue(pct)
        self.status_bar.showMessage(msg)

    def on_scan_finished(self, results: List[VideoRecording], sys_name: str):
        self.btn_scan.setEnabled(True)
        self.progress_bar.hide()

        self.detected_system = sys_name
        self.lbl_sys_badge.setText(f"SYSTEM: {sys_name.upper()}")

        self.all_recordings = results
        self.apply_filters()
        self.update_telemetry()

        self.status_bar.showMessage(f"Forensic scan complete. {len(results)} clean single-channel streams indexed.")

        if self.displayed_recordings:
            self.table_widget.selectRow(0)

    def update_telemetry(self):
        count = len(self.all_recordings)
        self.chip_count.setText(f"📊 Total Streams: {count}")

        total_bytes = sum(r.size_bytes for r in self.all_recordings)
        total_gb = round(total_bytes / (1024**3), 2)
        self.chip_size.setText(f"💾 Total Capacity: {total_gb} GB")

        channels = sorted(list({r.channel for r in self.all_recordings}))
        self.chip_channels.setText(f"📹 Active Cameras: {len(channels)} Channels")

        if self.all_recordings:
            newest = self.all_recordings[0].start_time.strftime("%Y-%m-%d %H:%M")
            oldest = self.all_recordings[-1].start_time.strftime("%Y-%m-%d %H:%M")
            self.chip_range.setText(f"⏱️ Timeline: {newest} ➔ {oldest}")
        else:
            self.chip_range.setText("⏱️ Timeline: None")

    def on_scan_failed(self, error: str):
        self.btn_scan.setEnabled(True)
        self.progress_bar.hide()
        QMessageBox.critical(self, "Forensic Scan Error", f"Unable to read physical sectors:\n\n{error}")

    def apply_filters(self):
        query = self.search_box.text().strip().lower()
        target_ch = self.cam_combo.currentData()
        clean_q = query.replace("-", "").replace("/", "")

        filtered = []
        for r in self.all_recordings:
            if target_ch != 0 and r.channel != target_ch:
                continue

            if query:
                r_ymd = r.start_time.strftime("%Y%m%d")
                r_iso = r.start_time.strftime("%Y-%m-%d")
                r_fname = r.file_name.lower()
                r_cam = f"ch{r.channel}"

                match = (
                    clean_q in r_ymd
                    or query in r_iso
                    or query in r_fname
                    or query in r_cam
                    or query in f"channel {r.channel}"
                    or query in r.start_time.strftime("%H:%M")
                )
                if not match:
                    continue

            filtered.append(r)

        self.populate_table(filtered)

    def populate_table(self, recordings: List[VideoRecording]):
        self.displayed_recordings = recordings
        self.table_widget.setRowCount(len(recordings))

        for row, rec in enumerate(recordings):
            chk = QCheckBox()
            chk_widget = QWidget()
            layout = QHBoxLayout(chk_widget)
            layout.addWidget(chk)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            self.table_widget.setCellWidget(row, 0, chk_widget)

            self.table_widget.setItem(row, 1, QTableWidgetItem(rec.system_type))
            self.table_widget.setItem(row, 2, QTableWidgetItem(rec.file_name))
            self.table_widget.setItem(row, 3, QTableWidgetItem(f"Camera {rec.channel:02d}"))
            self.table_widget.setItem(row, 4, QTableWidgetItem(rec.start_time.strftime("%Y-%m-%d %H:%M:%S")))
            self.table_widget.setItem(row, 5, QTableWidgetItem(rec.end_time.strftime("%Y-%m-%d %H:%M:%S")))
            self.table_widget.setItem(row, 6, QTableWidgetItem(rec.duration_str))
            self.table_widget.setItem(row, 7, QTableWidgetItem(f"{rec.size_mb} MB"))
            self.table_widget.setItem(row, 8, QTableWidgetItem(str(rec.start_lba)))

        self.lbl_table_title.setText(f"SURVEILLANCE STREAM INDEX — {len(recordings)} RECORDINGS (NEWEST FIRST)")

    def on_row_selected(self):
        row = self.table_widget.currentRow()
        if 0 <= row < len(self.displayed_recordings):
            rec = self.displayed_recordings[row]
            self.selected_recording = rec
            self.update_preview_panel(rec)

    def update_preview_panel(self, rec: VideoRecording):
        html = f"""
        <div style='line-height: 1.6; font-size: 11px;'>
            <span style='color: #00f5ff; font-weight: bold;'>TARGET STREAM:</span> {rec.file_name}<br>
            <span style='color: #00f5ff; font-weight: bold;'>ARCHITECTURE:</span> {rec.system_type}<br>
            <span style='color: #00f5ff; font-weight: bold;'>CHANNEL:</span> Camera {rec.channel:02d} (Demuxed Stream)<br>
            <span style='color: #00f5ff; font-weight: bold;'>START TIME:</span> {rec.start_time.strftime('%Y-%m-%d %H:%M:%S')}<br>
            <span style='color: #00f5ff; font-weight: bold;'>END TIME:</span> {rec.end_time.strftime('%Y-%m-%d %H:%M:%S')}<br>
            <span style='color: #00f5ff; font-weight: bold;'>DURATION:</span> {rec.duration_str}<br>
            <span style='color: #00f5ff; font-weight: bold;'>EST. SIZE:</span> {rec.size_mb} MB<br>
            <span style='color: #00f5ff; font-weight: bold;'>SECTOR LBA:</span> {rec.start_lba} &rarr; {rec.end_lba}<br>
        </div>
        """
        self.info_box.setHtml(html)
        self.lbl_preview_screen.setText("DECODING CAMERA KEYFRAME...")
        self.lbl_rec_indicator.setText(f"LIVE ● [CAM {rec.channel:02d}]")

        drive_path = self.drive_combo.currentData()
        if drive_path:
            self.prev_worker = PreviewWorker(drive_path, rec.start_lba, rec.channel, rec.file_id)
            self.prev_worker.frame_ready.connect(self.on_frame_ready)
            self.prev_worker.start()

    def on_frame_ready(self, img_bytes: bytes, file_id: str):
        if self.selected_recording and self.selected_recording.file_id == file_id:
            img = QImage()
            if img.loadFromData(img_bytes):
                pixmap = QPixmap.fromImage(img)
                scaled = pixmap.scaled(
                    self.lbl_preview_screen.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.lbl_preview_screen.setPixmap(scaled)
            else:
                self.lbl_preview_screen.setText("KEYFRAME RENDERED. READY TO PLAY.")

    def play_selected_clip(self):
        if not self.selected_recording:
            QMessageBox.information(self, "Notice", "Please select a recording from the table first.")
            return

        rec = self.selected_recording
        drive_path = self.drive_combo.currentData()
        temp_dir = tempfile.gettempdir()

        self.status_bar.showMessage(f"Buffering Channel {rec.channel} stream for live playback...")
        try:
            exporter = DirectStreamExporter(drive_path)
            preview_rec = VideoRecording(
                system_type=rec.system_type,
                channel=rec.channel,
                start_time=rec.start_time,
                end_time=rec.end_time,
                start_lba=rec.start_lba,
                end_lba=rec.start_lba + 16384,
                size_bytes=8 * 1024 * 1024,
                event_type=rec.event_type,
                file_id=rec.file_id,
                file_name="preview_" + rec.file_name,
                stream_type=rec.stream_type
            )
            raw_clip = exporter.export_recording(preview_rec, temp_dir)
            if raw_clip and os.path.exists(raw_clip):
                os.startfile(raw_clip)
                self.status_bar.showMessage(f"Playing Channel {rec.channel} stream: {rec.file_name}")
            else:
                QMessageBox.warning(self, "Playback Warning", "Could not buffer stream.")
        except Exception as e:
            QMessageBox.warning(self, "Playback Error", f"Error launching player: {e}")

    def save_single_recording(self):
        if not self.selected_recording:
            QMessageBox.information(self, "Notice", "Please select a recording first.")
            return

        rec = self.selected_recording
        out_dir = QFileDialog.getExistingDirectory(self, f"Dump Channel {rec.channel} Bitstream to...")
        if out_dir:
            self.do_export([rec], out_dir)

    def toggle_select_all(self):
        new_state = True
        first_widget = self.table_widget.cellWidget(0, 0)
        if first_widget:
            chk = first_widget.findChild(QCheckBox)
            if chk and chk.isChecked():
                new_state = False

        for row in range(self.table_widget.rowCount()):
            w = self.table_widget.cellWidget(row, 0)
            if w:
                chk = w.findChild(QCheckBox)
                if chk:
                    chk.setChecked(new_state)

    def export_selected(self):
        selected = []
        for row in range(self.table_widget.rowCount()):
            w = self.table_widget.cellWidget(row, 0)
            if w:
                chk = w.findChild(QCheckBox)
                if chk and chk.isChecked():
                    selected.append(self.displayed_recordings[row])

        if not selected:
            QMessageBox.information(self, "No Selection", "Please check at least one recording in the table.")
            return

        out_dir = QFileDialog.getExistingDirectory(self, f"Direct Dump {len(selected)} Streams to...")
        if out_dir:
            self.do_export(selected, out_dir)

    def do_export(self, recs: List[VideoRecording], out_dir: str):
        drive_path = self.drive_combo.currentData()
        self.progress_bar.show()
        self.btn_export.setEnabled(False)

        self.exp_worker = ExportWorker(drive_path, recs, out_dir)
        self.exp_worker.progress.connect(lambda pct, msg: (self.progress_bar.setValue(pct), self.status_bar.showMessage(msg)))
        self.exp_worker.finished.connect(self.on_export_finished)
        self.exp_worker.start()

    def on_export_finished(self, count: int):
        self.progress_bar.hide()
        self.btn_export.setEnabled(True)
        self.status_bar.showMessage(f"Direct stream dump complete. {count} single-channel bitstreams saved.")
        QMessageBox.information(
            self, "Forensic Dump Complete",
            f"Successfully exported {count} pure single-channel CCTV bitstreams.\n\n"
            "Streams were dumped directly to disk with zero transcoding delay, accompanied by SHA-256 evidentiary hash manifests."
        )
