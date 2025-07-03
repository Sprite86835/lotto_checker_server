# Basis-Image mit Python
FROM python:3.11-slim

# Tesseract und Abhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean

# Arbeitsverzeichnis setzen
WORKDIR /app

# Projektdateien kopieren
COPY . /app

# Python-Abhängigkeiten installieren
RUN pip install --no-cache-dir -r requirements.txt

# Flask-Port setzen
ENV PORT=5000

# Startbefehl
CMD ["python", "app.py"]
