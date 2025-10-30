#!/usr/bin/env python3
"""
TỰ ĐỘNG CÀI ĐẶT DDoS DETECTOR PRO
- Kiểm tra trước khi cài (không cài lại nếu đã có)
- Hỗ trợ: Windows & Ubuntu
"""

import os
import sys
import platform
import subprocess
import time
from pathlib import Path

# ==============================
# CẤU HÌNH
# ==============================
BASE_DIR = Path(__file__).parent.resolve()
PYTHON_SCRIPT = BASE_DIR / "ddos_detector_pro.py"
BAT_FILE = BASE_DIR / "Start_DDoS_Detector.bat"
SH_FILE = BASE_DIR / "start_ddos.sh"
ENV_FILE = BASE_DIR / ".env"
SYSTEM = platform.system()

# ==============================
# NỘI DUNG FILE (giống trước)
# ==============================
PYTHON_CODE = '''#!/usr/bin/env python3
# [NỘI DUNG ddos_detector_pro.py - ĐÃ CÓ Ở TRÊN] (giữ nguyên)
'''  # ← Dán toàn bộ code Python từ trước vào đây

BAT_CODE = '''@echo off
chcp 65001 >nul
title DDoS Detector Pro
color 0A
echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║               DDoS DETECTOR PRO - KHỞI ĐỘNG               ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

python --version >nul 2>&1 || (echo [LỖI] Python chưa cài! & pause & exit)
if not exist "ddos_detector_pro.py" (echo [LỖI] Thiếu file .py & pause & exit)
if not exist ".env" (echo [CẢNH BÁO] Tạo file .env & pause)

echo Cài thư viện...
pip install --quiet psutil scapy requests python-dotenv

echo.
echo  ĐANG CHẠY...
python ddos_detector_pro.py
'''

SH_CODE = '''#!/bin/bash
clear
echo "=================================="
echo "   DDoS DETECTOR PRO - UBUNTU     "
echo "=================================="

[ -f "ddos_detector_pro.py" ] || { echo "[LỖI] Thiếu file .py"; exit 1; }
[ -f ".env" ] || echo "[CẢNH BÁO] Tạo file .env với ABUSEIPDB_KEY=..."

pip3 list | grep -q psutil || pip3 install --quiet psutil scapy requests python-dotenv

echo "ĐANG KHỞI ĐỘNG..."
sudo python3 ddos_detector_pro.py
'''

# ==============================
# HÀM KIỂM TRA
# ==============================
def run_cmd(cmd, shell=False, capture=True):
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=capture, text=True)
        return result.returncode == 0, result.stdout if capture else ""
    except:
        return False, ""

def pip_installed(pkg):
    return run_cmd([sys.executable, "-m", "pip", "show", pkg], capture=False)[0]

def file_exists(path):
    return path.exists()

def tcpdump_installed():
    return run_cmd(["which", "tcpdump"], shell=True)[0]

# ==============================
# CÀI ĐẶT CÓ KIỂM TRA
# ==============================
def install_pip_packages():
    print("Kiểm tra thư viện Python...")
    pkgs = ["psutil", "scapy", "requests", "python-dotenv"]
    for pkg in pkgs:
        if pip_installed(pkg):
            print(f"   [ĐÃ CÓ] {pkg}")
        else:
            print(f"   [CÀI] {pkg}...")
            run_cmd([sys.executable, "-m", "pip", "install", "--quiet", pkg])

def install_system_deps():
    print(f"Kiểm tra hệ điều hành: {SYSTEM}")
    if SYSTEM == "Windows":
        print("   [THÔNG BÁO] Npcap: Cài thủ công tại https://nmap.org/npcap/")
    elif SYSTEM == "Linux":
        if tcpdump_installed():
            print("   [ĐÃ CÓ] tcpdump")
        else:
            print("   [CÀI] tcpdump...")
            run_cmd(["sudo", "apt", "update", "-y"])
            run_cmd(["sudo", "apt", "install", "-y", "tcpdump"])

def create_files():
    print("Kiểm tra và tạo file...")
    
    # Python script
    if file_exists(PYTHON_SCRIPT):
        print("   [ĐÃ CÓ] ddos_detector_pro.py")
    else:
        PYTHON_SCRIPT.write_text(PYTHON_CODE, encoding='utf-8')
        print("   [TẠO] ddos_detector_pro.py")

    # .env
    if file_exists(ENV_FILE):
        print("   [ĐÃ CÓ] .env")
    else:
        ENV_FILE.write_text("ABUSEIPDB_KEY=your_api_key_here\n", encoding='utf-8')
        print("   [TẠO] .env (sửa key sau)")

    # .bat hoặc .sh
    if SYSTEM == "Windows":
        if file_exists(BAT_FILE):
            print("   [ĐÃ CÓ] Start_DDoS_Detector.bat")
        else:
            BAT_FILE.write_text(BAT_CODE, encoding='utf-8')
            print("   [TẠO] Start_DDoS_Detector.bat")
    else:
        if file_exists(SH_FILE):
            print("   [ĐÃ CÓ] start_ddos.sh")
        else:
            SH_FILE.write_text(SH_CODE, encoding='utf-8')
            SH_FILE.chmod(SH_FILE.stat().st_mode | 0o755)
            print("   [TẠO] start_ddos.sh (đã +x)")

def setup_autostart():
    print("Kiểm tra tự động khởi động...")
    if SYSTEM == "Windows":
        startup = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        shortcut = startup / "DDoS_Detector_Pro.lnk"
        if shortcut.exists():
            print("   [ĐÃ CÓ] Shortcut trong Startup")
        else:
            try:
                import winshell
                from win32com.client import Dispatch
                shell = Dispatch('WScript.Shell')
                sc = shell.CreateShortCut(str(shortcut))
                sc.Targetpath = str(BAT_FILE)
                sc.WorkingDirectory = str(BASE_DIR)
                sc.IconLocation = str(sys.executable)
                sc.save()
                print("   [TẠO] Shortcut trong Startup")
            except Exception as e:
                print(f"   [THỦ CÔNG] Tạo shortcut .bat vào shell:startup")
    else:
        service_file = "/etc/systemd/system/ddos-detector.service"
        if Path(service_file).exists():
            print("   [ĐÃ CÓ] systemd service")
        else:
            user = os.getenv("SUDO_USER") or os.getenv("USER")
            service_content = f'''[Unit]
Description=DDoS Detector Pro
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={BASE_DIR}
ExecStart=/usr/bin/python3 {PYTHON_SCRIPT}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
'''
            try:
                with open(service_file, "w") as f:
                    f.write(service_content)
                run_cmd(["sudo", "systemctl", "daemon-reload"])
                run_cmd(["sudo", "systemctl", "enable", "ddos-detector.service"])
                print("   [TẠO] systemd service")
            except:
                print("   [THỦ CÔNG] Tạo file service")

# ==============================
# CHẠY CHÍNH
# ==============================
def main():
    print("="*60)
    print("    TỰ ĐỘNG CÀI ĐẶT DDoS DETECTOR PRO (CÓ KIỂM TRA)")
    print("="*60)

    install_pip_packages()
    install_system_deps()
    create_files()
    setup_autostart()

    print("\nHOÀN TẤT!")
    print(f"   Thư mục: {BASE_DIR}")
    print("   Sửa .env → ABUSEIPDB_KEY=your_real_key")
    print("   Lấy key: https://www.abuseipdb.com/account/api")

    if SYSTEM == "Windows":
        print("   → Chạy: Double-click Start_DDoS_Detector.bat")
    else:
        print("   → Chạy: ./start_ddos.sh")

    choice = input("\nKhởi động ngay? (y/N): ").strip().lower()
    if choice == 'y':
        if SYSTEM == "Windows":
            os.startfile(BAT_FILE)
        else:
            os.system(f"sudo python3 {PYTHON_SCRIPT}")

if __name__ == "__main__":
    main()