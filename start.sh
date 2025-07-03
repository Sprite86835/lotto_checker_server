#!/bin/bash
echo "🔧 Installiere benötigte Pakete..."
sudo apt update
sudo apt install -y python3-pip tesseract-ocr

echo "📦 Installiere Python-Abhängigkeiten..."
pip3 install -r requirements.txt

echo "🚀 Starte die Lotto-Checker API..."
python3 app.py
