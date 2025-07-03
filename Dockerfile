# Basis-Image mit Python 3.13 slim
FROM python:3.13-slim

# Systemabhängigkeiten installieren (libgl1 für OpenCV, tesseract für OCR)
RUN apt-get update && apt-get install -y \
    libgl1 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis im Container
WORKDIR /app

# Anforderungen kopieren und installieren
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Quellcode kopieren
COPY . .

# Port für Flask-Anwendung (Standard 5000)
EXPOSE 5000

# Startbefehl
CMD ["python", "app.py"]
