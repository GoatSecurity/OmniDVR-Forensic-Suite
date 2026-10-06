@echo off
title OmniDVR Forensic Suite - GoatSecurity
cd /d "%~dp0"
echo ===================================================
echo     OmniDVR Forensic Suite - by GoatSecurity
echo ===================================================
echo Checking Administrator privileges...
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with Administrator privileges.
    python main.py
) else (
    echo [!] Requesting Administrator privileges via UAC...
    powershell -Command "Start-Process python -ArgumentList 'main.py' -Verb RunAs"
)
