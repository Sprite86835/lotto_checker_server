from flask import Flask, request, send_file
from flask_cors import CORS
import pytesseract
import cv2
import numpy as np
from PIL import Image
from pytesseract import Output
import io
import re
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return '✅ Lotto Checker API läuft!'

@app.route('/check_lotto', methods=['POST'])
def check_lotto():
    if 'image' not in request.files or 'numbers' not in request.form:
        return {'error': 'Bild oder Zahlen fehlen'}, 400

    # Eingaben holen
    image_file = request.files['image']
    user_numbers = [num.strip() for num in request.form['numbers'].split(',') if num.strip().isdigit()]
    user_set = set(user_numbers)

    # Bild laden und konvertieren
    img_pil = Image.open(image_file).convert('RGB')
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    # OCR durchführen
    data = pytesseract.image_to_data(img_cv, config='--psm 6', output_type=Output.DICT)

    recognized = []

    for i in range(len(data['text'])):
        raw_text = data['text'][i].strip()
        if not raw_text:
            continue

        # Alle ein- oder zweistelligen Zahlen extrahieren
        numbers_in_text = re.findall(r'\b\d{1,2}\b', raw_text)
        if not numbers_in_text:
            continue

        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]

        for number in numbers_in_text:
            recognized.append(number)
            color = (0, 0, 255) if number in user_set else (255, 0, 0)
            cv2.rectangle(img_cv, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img_cv, number, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # Ergebnisbild zurückgeben
    result_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    result_pil = Image.fromarray(result_rgb)
    buffer = io.BytesIO()
    result_pil.save(buffer, format='JPEG')
    buffer.seek(0)

    return send_file(buffer, mimetype='image/jpeg')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
