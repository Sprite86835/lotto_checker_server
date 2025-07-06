# Basis-Image mit Python und minimalem Debian
FROM python:3.10-slim

# Systempakete installieren, inkl. Tesseract und OpenCV-Abhängigkeiten
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis setzen
WORKDIR /app

# Kopiere requirements, falls du eines hast (optional)
# COPY requirements.txt .
# RUN pip install -r requirements.txt

# Oder direkt benötigte Pakete installieren
RUN pip install flask flask-cors pytesseract opencv-python pillow

# Projektdateien kopieren
COPY . .

# Port für Render (Render sucht automatisch $PORT)
ENV PORT=5000

# Startbefehl
CMD ["python", "app.py"]
