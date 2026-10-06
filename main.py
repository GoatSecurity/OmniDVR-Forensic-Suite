"""
OmniDVR Forensic Suite - Application Entry Point
Author: GoatSecurity (GitHub: GoatSecurity)
License: MIT
"""

import sys
import os

# Ensure package roots are resolved
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.disk_io import is_admin, request_admin_elevation


def main():
    if not is_admin():
        print("[*] OmniDVR requires Administrator rights to access raw physical sectors.")
        elevated = request_admin_elevation()
        if not elevated:
            print("[!] Elevation cancelled. Exiting.")
            sys.exit(1)
        return

    from PyQt6.QtWidgets import QApplication
    from ui.main_window import OmniDVRMainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("OmniDVR Forensic Suite")
    app.setOrganizationName("GoatSecurity")

    window = OmniDVRMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
