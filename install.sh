#!/bin/bash
echo "Installing DDoS Protection on Linux/WSL..."
mkdir -p ~/ddos_pro && cd ~/ddos_pro
curl -fsSL https://raw.githubusercontent.com/victlee69/ddos-protection/main/setup_ddos_pro.py -o setup.py
python3 setup.py <<< "y"
echo "Done! Protection is running."
