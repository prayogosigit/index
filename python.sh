#!/bin/bash

set -e

echo "🔧 Update dan install dependencies..."
sudo apt update -y
sudo apt install -y software-properties-common curl

echo "📦 Menambahkan PPA untuk Python 3.11..."
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update -y

echo "🐍 Menginstal Python 3.11 dan pip..."
sudo apt install -y python3.11 python3.11-venv python3.11-dev
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.11

echo "🔗 Membuat alias python & pip -> python3.11"
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1
sudo update-alternatives --install /usr/bin/pip pip /usr/local/bin/pip3.11 1

echo "✅ Selesai. Versi:"
python --version
pip --version
