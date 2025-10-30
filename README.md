# DDoS Detector Pro – 1-Click DDoS Protection  

[![GitHub stars](https://img.shields.io/github/stars/victlee69/ddos-protection?style=social)](https://github.com/victlee69/ddos-protection)
[![GitHub forks](https://img.shields.io/github/forks/victlee69/ddos-protection)](https://github.com/victlee69/ddos-protection)
[![License](https://img.shields.io/github/license/victlee69/ddos-protection)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)

**Real-time SYN/UDP/ICMP flood detection + automatic IP blocking** – works on Windows & Linux.

> **Deploy on any machine in 10 seconds with a single command!**

---

## Features

| Feature | Description |
|---------|-------------|
| **Real-time Monitoring** | CPU, RAM, connections, packet rates |
| **DDoS Detection** | SYN Flood, UDP Flood, ICMP Flood |
| **Top 5 Attacker IPs** | Live ranking |
| **Auto IP Blocking** | `iptables` (Linux) / `netsh` (Windows) |
| **AbuseIPDB Integration** | Blocks only high-confidence malicious IPs |
| **Auto Unblock** | 5-minute temporary blocks |
| **Autostart** | systemd (Linux) / Startup folder (Windows) |
| **Console-Only** | No web UI – lightweight & fast |

---

## 1-Click Install

```bash
curl -fsSL https://raw.githubusercontent.com/victlee69/ddos-protection/main/install.sh | bash
