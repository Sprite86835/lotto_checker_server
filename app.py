from flask import Flask, request, send_file
from flask_cors import CORS
import pytesseract
from pytesseract import Output
import cv2
import numpy as np
import io

app = Flask(__name__)
CORS(app)

@app.route('/check_lotto', methods=['POST'])
def check_lotto():
    if 'image' not in request.files or 'numbers' not in request.form:
        return "Missing image or numbers", 400

    # Eingabedaten laden
    file = request.files['image']
    numbers_str = request.form['numbers']
    print(f"Empfangene Zahlen: {numbers_str}")
    drawn_numbers = [num.strip() for num in numbers_str.split(',') if num.strip().isdigit()]
    print(f"Parsed Zahlen: {drawn_numbers}")

    # Bild verarbeiten
    in_memory_file = io.BytesIO()
    file.save(in_memory_file)
    data = np.frombuffer(in_memory_file.getvalue(), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)

    # OCR-Konfiguration
    config = '--psm 6'
    data = pytesseract.image_to_data(img, config=config, output_type=Output.DICT)
    print(f"OCR Daten: {data['text']}")

    for i, text in enumerate(data['text']):
        text = text.strip()
        if not text.isdigit():
            continue
        if text in drawn_numbers:
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            print(f"Gefundene Zahl: {text} bei Position: ({x},{y},{w},{h})")
            # Zeichne ein Rechteck um gefundene Zahlen
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Bild zurücksenden
    _, img_encoded = cv2.imencode('.jpg', img)
    return send_file(
        io.BytesIO(img_encoded.tobytes()),
        mimetype='image/jpeg',
        as_attachment=False,
        download_name='result.jpg'
    )

@app.route('/')
def index():
    return "Lotto Checker Server is running", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
