"""
OmniDVR Forensic Suite - Next-Gen Cyber-Forensic Glassmorphism Stylesheet
Ultra-detailed styling covering every Qt widget, custom titlebar, scrollbars, tabs, badges, tables, and buttons.
Author: GoatSecurity (GitHub: GoatSecurity)
License: MIT
"""

FORENSIC_THEME = """
/* ==========================================================================
   GLOBAL BASE & TYPOGRAPHY
   ========================================================================== */
QMainWindow, QDialog {
    background-color: #08090d;
    color: #e2e8f0;
    border: 1px solid #1e2436;
    border-radius: 12px;
}

QWidget {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'SF Pro Display', Roboto, 'Helvetica Neue', Arial;
    font-size: 12px;
    color: #94a3b8;
    selection-background-color: #00f5ff;
    selection-color: #08090d;
}

/* ==========================================================================
   CUSTOM TITLEBAR & WINDOW CONTROLS
   ========================================================================== */
QFrame#customTitleBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #12151f, stop:1 #0c0e14);
    border-top-left-radius: 11px;
    border-top-right-radius: 11px;
    border-bottom: 1px solid #1a2030;
    padding: 4px 12px;
    min-height: 38px;
}

QLabel#titleAppText {
    color: #f1f5f9;
    font-weight: 800;
    font-size: 13px;
    letter-spacing: 0.8px;
}

QLabel#titleGoatBadge {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #ec4899);
    color: #ffffff;
    font-weight: 900;
    font-size: 9px;
    padding: 3px 8px;
    border-radius: 4px;
    letter-spacing: 1px;
}

/* Window Control Buttons (Min, Max, Close) */
QPushButton#winMinBtn, QPushButton#winMaxBtn, QPushButton#winCloseBtn {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    font-size: 11px;
    font-weight: bold;
    min-width: 32px;
    min-height: 26px;
    max-width: 32px;
    max-height: 26px;
    color: #94a3b8;
    padding: 0px;
}

QPushButton#winMinBtn:hover {
    background-color: #1a2030;
    color: #00f5ff;
}

QPushButton#winMaxBtn:hover {
    background-color: #1a2030;
    color: #00f5ff;
}

QPushButton#winCloseBtn:hover {
    background-color: #e11d48;
    color: #ffffff;
}

QPushButton#winCloseBtn:pressed {
    background-color: #be123c;
    color: #ffffff;
}

/* ==========================================================================
   NAVIGATION COMMAND BAR
   ========================================================================== */
QFrame#topNav {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0f121a, stop:1 #0a0c11);
    border-bottom: 1px solid #161b26;
    padding: 8px 16px;
}

QLabel#navLabel {
    color: #64748b;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

/* ==========================================================================
   TELEMETRY & STATS RIBBON
   ========================================================================== */
QFrame#telemetryBar {
    background-color: #07080c;
    border-bottom: 1px solid #131722;
    padding: 6px 16px;
}

QLabel#chipLabel {
    background-color: #0e1118;
    color: #94a3b8;
    border: 1px solid #1a2030;
    border-radius: 6px;
    padding: 4px 11px;
    font-size: 11px;
    font-weight: 600;
}

QLabel#chipLabel:hover {
    border: 1px solid #00f5ff;
    color: #e2e8f0;
}

QLabel#sysBadge {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #082f49, stop:1 #0c4a6e);
    color: #38bdf8;
    border: 1px solid #0284c7;
    border-radius: 6px;
    padding: 5px 14px;
    font-weight: 800;
    font-size: 11px;
    letter-spacing: 0.5px;
}

/* ==========================================================================
   INPUTS & COMBOBOXES
   ========================================================================== */
QComboBox {
    background-color: #11141c;
    color: #f1f5f9;
    border: 1px solid #1e2436;
    border-radius: 7px;
    padding: 6px 14px;
    min-width: 190px;
    font-size: 12px;
    font-weight: 600;
}

QComboBox:hover {
    border: 1px solid #00f5ff;
    background-color: #141824;
}

QComboBox:focus {
    border: 1px solid #00f5ff;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #11141c;
    color: #f1f5f9;
    selection-background-color: #00f5ff;
    selection-color: #08090d;
    border: 1px solid #1e2436;
    border-radius: 6px;
    outline: none;
    padding: 4px;
}

QLineEdit {
    background-color: #11141c;
    color: #ffffff;
    border: 1px solid #1e2436;
    border-radius: 7px;
    padding: 6px 14px;
    font-size: 12px;
}

QLineEdit:hover {
    border: 1px solid #2a344d;
    background-color: #141824;
}

QLineEdit:focus {
    border: 1px solid #00f5ff;
    background-color: #141824;
}

/* ==========================================================================
   ACTION BUTTONS
   ========================================================================== */
QPushButton {
    background-color: #131722;
    color: #f1f5f9;
    border: 1px solid #1e2436;
    border-radius: 7px;
    padding: 7px 16px;
    font-weight: 700;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #1a2030;
    border: 1px solid #00f5ff;
    color: #00f5ff;
}

QPushButton:pressed {
    background-color: #0e121a;
    border: 1px solid #0284c7;
}

QPushButton#btnScan {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #00f5ff);
    color: #06090f;
    font-weight: 900;
    border: none;
    padding: 8px 22px;
    border-radius: 7px;
    letter-spacing: 0.5px;
}

QPushButton#btnScan:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #38bdf8, stop:1 #67e8f9);
}

QPushButton#btnExport {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981);
    color: #ffffff;
    font-weight: 900;
    border: none;
    padding: 8px 22px;
    border-radius: 7px;
    letter-spacing: 0.5px;
}

QPushButton#btnExport:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #34d399);
}

QPushButton#btnPlay {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d97706, stop:1 #f59e0b);
    color: #06090f;
    font-weight: 900;
    border: none;
    padding: 10px 22px;
    border-radius: 7px;
    font-size: 12px;
    letter-spacing: 0.5px;
}

QPushButton#btnPlay:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #fbbf24);
}

/* ==========================================================================
   FORENSIC DATA TABLE
   ========================================================================== */
QTableWidget {
    background-color: #0a0b10;
    alternate-background-color: #0e1017;
    color: #e2e8f0;
    border: 1px solid #161b26;
    border-radius: 9px;
    gridline-color: #121520;
    selection-background-color: #0c2b3d;
    selection-color: #00f5ff;
    outline: none;
}

QTableWidget::item {
    padding: 7px 10px;
    border-bottom: 1px solid #10131a;
}

QTableWidget::item:hover {
    background-color: #131722;
}

QTableWidget::item:selected {
    background-color: #0c2b3d;
    color: #00f5ff;
    font-weight: 700;
}

QHeaderView::section {
    background-color: #0d0f15;
    color: #00f5ff;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    border: none;
    border-bottom: 2px solid #161b26;
    border-right: 1px solid #12151f;
    padding: 9px 12px;
    font-size: 11px;
}

/* ==========================================================================
   CHECKBOXES
   ========================================================================== */
QCheckBox {
    spacing: 7px;
    color: #cbd5e1;
    font-size: 12px;
}

QCheckBox::indicator {
    width: 17px;
    height: 17px;
    border: 1px solid #2a344d;
    border-radius: 4px;
    background-color: #0e1118;
}

QCheckBox::indicator:hover {
    border: 1px solid #00f5ff;
}

QCheckBox::indicator:checked {
    background-color: #00f5ff;
    border: 1px solid #00f5ff;
    image: none;
}

/* ==========================================================================
   CUSTOM ULTRA-THIN SCROLLBARS
   ========================================================================== */
QScrollBar:vertical {
    background-color: #08090d;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #1a2030;
    min-height: 25px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #00f5ff;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #08090d;
    height: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background-color: #1a2030;
    min-width: 25px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #00f5ff;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ==========================================================================
   SURVEILLANCE HUD MONITOR DOCK
   ========================================================================== */
QFrame#previewCard {
    background-color: #0d0f15;
    border: 1px solid #1a2030;
    border-radius: 11px;
    padding: 16px;
}

QLabel#previewScreen {
    background-color: #050608;
    border: 2px solid #171c26;
    border-radius: 9px;
}

QTextEdit#hudInfoBox {
    background-color: #07080c;
    border: 1px solid #161b26;
    border-radius: 7px;
    color: #94a3b8;
    font-family: 'Cascadia Code', Consolas, 'Courier New', monospace;
    font-size: 11px;
    padding: 8px;
}

/* ==========================================================================
   PROGRESS BAR & STATUS BAR
   ========================================================================== */
QProgressBar {
    border: none;
    border-radius: 3px;
    text-align: center;
    background-color: #0b0c10;
    color: #ffffff;
    font-size: 10px;
    font-weight: 800;
    min-height: 12px;
    max-height: 12px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #00f5ff);
    border-radius: 3px;
}

QStatusBar {
    background-color: #08090d;
    color: #64748b;
    border-top: 1px solid #131722;
    border-bottom-left-radius: 11px;
    border-bottom-right-radius: 11px;
    font-size: 11px;
    padding: 5px 14px;
}

/* ==========================================================================
   TOOLTIPS
   ========================================================================== */
QToolTip {
    background-color: #0f121a;
    color: #00f5ff;
    border: 1px solid #00f5ff;
    border-radius: 5px;
    padding: 5px 10px;
    font-size: 11px;
    font-weight: 600;
}
"""
