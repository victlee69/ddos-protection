#!/usr/bin/env python3
"""
DDoS Detector Pro - Real-time Console Monitor
Hợp nhất + cải tiến từ 2 script gốc
Tính năng: CPU, RAM, Connections, Packet Rates, Top IPs, Auto Block, Alerts
"""

import sys
import time
import threading
import logging
import subprocess
import os
import platform
from collections import defaultdict, deque
from datetime import datetime
from dotenv import load_dotenv
import psutil
import requests
from scapy.all import sniff, get_if_list

# ==============================
# LOAD ENV + CONFIG
# ==============================
load_dotenv()

ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_KEY")
if not ABUSEIPDB_API_KEY:
    print("[FATAL] ABUSEIPDB_KEY not found in .env file!")
    sys.exit(1)

THRESHOLDS = {
    'SYN_PER_SEC': 100,
    'UDP_PER_SEC': 200,
    'ICMP_PER_SEC': 100,
    'CONNECTIONS': 1000,
    'BLOCK_DURATION': 300,  # 5 phút
    'MIN_PACKETS_TO_BLOCK': 50
}

WHITELIST_IPS = [
    "127.0.0.1", "192.168.", "10.", "172.16.", "172.17.", "172.18.",
    "8.8.8.8", "1.1.1.1",
    "104.16.", "104.17.", "104.18.", "104.19.", "104.20.",
    "216.58.", "216.137.", "216.239."
]

LOG_FILE = "ddos_protection.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    filemode='a'
)

# ==============================
# BLOCK IP SYSTEM
# ==============================
blocked_ips = {}
blocked_lock = threading.Lock()

def is_whitelisted(ip):
    return any(ip.startswith(prefix) for prefix in WHITELIST_IPS)

def check_abuseipdb(ip):
    try:
        r = requests.get(
            "https://api.abuseipdb.com/api/v2/check",
            params={'ipAddress': ip, 'maxAgeInDays': 90},
            headers={'Key': ABUSEIPDB_API_KEY, 'Accept': 'application/json'},
            timeout=5
        )
        data = r.json().get('data', {})
        score = data.get('abuseConfidenceScore', 0)
        return score > 70
    except Exception as e:
        logging.warning(f"AbuseIPDB failed for {ip}: {e}")
        return False

def block_ip(ip):
    if is_whitelisted(ip):
        return False
    with blocked_lock:
        if ip in blocked_ips:
            return False

    if not check_abuseipdb(ip):
        return False

    system = platform.system()
    try:
        if system == "Windows":
            cmd = ['netsh', 'advfirewall', 'firewall', 'add', 'rule',
                   f'name=DDoS_BLOCK_{ip}', 'dir=in', 'action=block', f'remoteip={ip}']
        elif system == "Linux":
            cmd = ['sudo', 'iptables', '-I', 'INPUT', '-s', ip, '-j', 'DROP']
        else:
            return False

        subprocess.run(cmd, check=True, capture_output=True)
        with blocked_lock:
            blocked_ips[ip] = time.time()
        logging.critical(f"BLOCKED IP: {ip}")
        return True
    except Exception as e:
        logging.error(f"Failed to block {ip}: {e}")
        return False

def unblock_ip(ip):
    system = platform.system()
    try:
        if system == "Windows":
            cmd = ['netsh', 'advfirewall', 'firewall', 'delete', 'rule', f'name=DDoS_BLOCK_{ip}']
        elif system == "Linux":
            cmd = ['sudo', 'iptables', '-D', 'INPUT', '-s', ip, '-j', 'DROP']
        else:
            return
        subprocess.run(cmd, check=True, capture_output=True)
        logging.info(f"UNBLOCKED IP: {ip}")
    except Exception as e:
        logging.error(f"Failed to unblock {ip}: {e}")

def cleanup_blocked_ips():
    while True:
        now = time.time()
        expired = []
        with blocked_lock:
            for ip, block_time in blocked_ips.items():
                if now - block_time > THRESHOLDS['BLOCK_DURATION']:
                    expired.append(ip)
            for ip in expired:
                del blocked_ips[ip]
        for ip in expired:
            unblock_ip(ip)
        time.sleep(60)

# ==============================
# PACKET MONITOR (Scapy)
# ==============================
class PacketMonitor:
    def __init__(self):
        self.syn_queue = deque(maxlen=300)
        self.udp_queue = deque(maxlen=300)
        self.icmp_queue = deque(maxlen=300)
        self.ip_counter = defaultdict(int)
        self.lock = threading.Lock()

    def packet_callback(self, packet):
        if not packet.haslayer('IP'):
            return
        src_ip = packet['IP'].src
        t = time.time()

        with self.lock:
            self.ip_counter[src_ip] += 1
            if packet.haslayer('TCP') and (packet['TCP'].flags & 0x02):  # SYN
                self.syn_queue.append((t, src_ip))
            elif packet.haslayer('UDP'):
                self.udp_queue.append((t, src_ip))
            elif packet.haslayer('ICMP'):
                self.icmp_queue.append((t, src_ip))

    def get_rate(self, queue):
        now = time.time()
        return len([t for t, _ in queue if now - t <= 1])

    def get_top_ips(self):
        with self.lock:
            top = sorted(self.ip_counter.items(), key=lambda x: x[1], reverse=True)[:5]
            self.ip_counter.clear()
            return top

# ==============================
# CONNECTION MONITOR (psutil)
# ==============================
def get_connection_stats():
    try:
        conns = psutil.net_connections(kind='inet')
        count_by_status = defaultdict(int)
        for c in conns:
            if c.status:
                count_by_status[c.status] += 1
        total = len(conns)
        return total, count_by_status
    except Exception as e:
        logging.error(f"Connection stats error: {e}")
        return 0, {}

# ==============================
# MAIN DISPLAY LOOP
# ==============================
def main():
    print("DDoS Detector Pro - Khởi động...")
    logging.info("DDoS Detector Pro started")

    # Chọn interface
    try:
        iface = next((i for i in get_if_list() if 'NPF' in i or 'eth' in i or 'wlan' in i), get_if_list()[0])
    except:
        print("[LỖI] Không tìm thấy interface mạng!")
        sys.exit(1)
    print(f"Đang theo dõi trên: {iface}")

    monitor = PacketMonitor()

    # Bắt đầu sniff
    sniff_thread = threading.Thread(
        target=sniff,
        kwargs={
            'iface': iface,
            'prn': monitor.packet_callback,
            'store': False,
            'filter': 'tcp or udp or icmp'
        },
        daemon=True
    )
    sniff_thread.start()

    # Bắt đầu dọn dẹp block
    threading.Thread(target=cleanup_blocked_ips, daemon=True).start()

    try:
        while True:
            # --- Thu thập dữ liệu ---
            syn_rate = monitor.get_rate(monitor.syn_queue)
            udp_rate = monitor.get_rate(monitor.udp_queue)
            icmp_rate = monitor.get_rate(monitor.icmp_queue)
            top_ips = monitor.get_top_ips()

            total_conns, conn_status = get_connection_stats()

            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent

            # --- Kiểm tra cảnh báo ---
            alerts = []
            if syn_rate > THRESHOLDS['SYN_PER_SEC']:
                alerts.append(f"SYN Flood ({syn_rate}/s)")
            if udp_rate > THRESHOLDS['UDP_PER_SEC']:
                alerts.append(f"UDP Flood ({udp_rate}/s)")
            if icmp_rate > THRESHOLDS['ICMP_PER_SEC']:
                alerts.append(f"ICMP Flood ({icmp_rate}/s)")
            if total_conns > THRESHOLDS['CONNECTIONS']:
                alerts.append(f"Connections High ({total_conns})")

            # --- Tự động block IP nguy hiểm ---
            if alerts:
                for ip, count in top_ips:
                    if count >= THRESHOLDS['MIN_PACKETS_TO_BLOCK'] and ip not in blocked_ips:
                        if not is_whitelisted(ip):
                            threading.Thread(target=block_ip, args=(ip,), daemon=True).start()

            # --- Hiển thị giao diện ---
            os.system('cls' if os.name == 'nt' else 'clear')
            print("="*70)
            print("        DDoS DETECTOR PRO - REAL-TIME MONITOR")
            print("="*70)
            print(f"{'Thời gian:':<12} {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'CPU:':<12} {cpu:>6.1f}%")
            print(f"{'RAM:':<12} {ram:>6.1f}%")
            print(f"{'Connections:':<12} {total_conns:>6}")
            print("-"*70)
            print(f"{'SYN/sec:':<12} {syn_rate:>6}  |  {'UDP/sec:':<12} {udp_rate:>6}  |  {'ICMP/sec:':<12} {icmp_rate:>6}")
            print("-"*70)
            print(" TOP 5 NGUY HIỂM (gói/giây):")
            for ip, count in top_ips:
                status = "BLOCKED" if ip in blocked_ips else "MONITORING"
                print(f"  {ip:<15} | {count:>6} pkt/s | {status}")
            print("-"*70)
            if alerts:
                print(" CẢNH BÁO: " + " | ".join(alerts))
            else:
                print(" TRẠNG THÁI: BÌNH THƯỜNG")
            print("-"*70)
            print(f"Đã chặn: {len(blocked_ips)} IP | Ctrl+C để dừng")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[THOÁT] Đã dừng giám sát.")
        logging.info("DDoS Detector Pro stopped by user")
        sys.exit(0)
    except Exception as e:
        logging.critical(f"Critical error: {e}")
        time.sleep(1)

if __name__ == "__main__":
    main()