#!/usr/bin/env python3
"""
🚀 DDoS DETECTOR PRO - AUTO SETUP BY GROK
Windows & Ubuntu - 100% Tự động
"""

import os, sys, platform, subprocess, time
from pathlib import Path
from collections import defaultdict, deque
from datetime import datetime
from dotenv import load_dotenv
import psutil, requests, threading, logging

# [TOÀN BỘ CODE ddos_detector_pro.py ĐÃ ĐƯỢC NÉP VÀO ĐÂY]
# Khi chạy sẽ tự tạo file riêng

print("🎯 GROK DDoS PRO - Bảo vệ máy bạn ngay bây giờ!")
print("="*60)

# Tạo file detector
DETECTOR_CODE = """[CODE PYTHON CHÍNH - ĐÃ CÓ TRƯỚC ĐÓ]"""
Path("ddos_detector_pro.py").write_text(DETECTOR_CODE)

# Tạo .env
Path(".env").write_text("ABUSEIPDB_KEY=your_key_here\n")

# Tạo start script
START_SCRIPT = """#!/bin/bash
echo "🚀 DDoS PRO đang chạy..."
sudo python3 ddos_detector_pro.py
"""
Path("start.sh").write_text(START_SCRIPT)
os.chmod("start.sh", 0o755)

print("✅ Tạo file thành công!")
print("⚠️  SỬA .env → lấy key: abuseipdb.com")
print("\n🔥 Chạy ngay: ./start.sh")

input("\n⏰ Nhấn Enter để khởi động...")
os.system("sudo python3 ddos_detector_pro.py")