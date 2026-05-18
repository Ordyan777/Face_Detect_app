#!/bin/bash

# ---=== by Catalyst77 ===---

set -e

echo "[INFO] Updating packages..."
sudo apt update


sleep 2
clear

sleep 2
echo "[INFO] Installing required libraries..."
sudo apt install -y \
build-essential libssl-dev libffi-dev libsqlite3-dev \
libreadline-dev libbz2-dev libncurses5-dev libncursesw5-dev \
liblzma-dev zlib1g-dev libgdbm-dev libnss3-dev wget \
tk-dev uuid-dev cmake libopenblas-dev liblapack-dev \
libx11-dev libgtk-3-dev
clear
sleep 2

echo "[INFO] Downloading Python 3.10..."
cd /tmp
wget https://www.python.org/ftp/python/3.10.14/Python-3.10.14.tgz
clear
sleep 2

echo "[INFO] Extracting archive..."
tar -xf Python-3.10.14.tgz
cd Python-3.10.14
sleep 2
clear

echo "[INFO] Configuring build..."
./configure --enable-optimizations
sleep 2
clear

echo "[INFO] Building Python..."
make -j$(nproc)
sleep 2
clear

echo "[INFO] Installing Python 3.10.14 ..."
sudo make altinstall
sleep 2
clear


echo "[INFO] Checking versions..."
python3.10 --version
pip3.10 --version
sleep 2
clear


echo "[INFO] Upgrading pip..."
pip3.10 install --upgrade pip
sleep 2
clear


echo "[INFO] Cleaning temporary files..."
cd /tmp
rm -rf Python-3.10.14*
sleep 2 
clear

echo "[SUCCESS] Python 3.10.14 installed successfully!"

sleep 3
clear

