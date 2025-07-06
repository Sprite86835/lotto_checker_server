from flask import Flask, request, Response
from flask_cors import CORS
import pytesseract
import cv2
import numpy as np
from PIL import Image
from pytesseract import Output
from io import BytesIO
from email.generator import BytesGenerator
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
import json
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

    image_file = request.files['image']
    user_numbers = [num.strip().zfill(2) for num in request.form['numbers'].split(',') if num.strip().isdigit()]

    # 🖼️ Bild einlesen und vorbereiten
    img_pil = Image.open(image_file).convert('RGB')
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY_INV)

    # 🔍 OCR-Konfiguration: Nur Ziffern, Blockweise Analyse
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
    data = pytesseract.image_to_data(thresh, config=custom_config, output_type=Output.DICT)

    recognized = []

    for i in range(len(data['text'])):
        raw_text = data['text'][i].strip()
        if not raw_text.isdigit():
            continue

        x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]

        # 👉 Split bei langen Blöcken z.B. "50556266"
        if len(raw_text) > 2:
            for j in range(0, len(raw_text) - 1, 2):
                two_digit = raw_text[j:j + 2]
                if len(two_digit) == 2:
                    recognized.append(two_digit)
                    color = (0, 0, 255) if two_digit in user_numbers else (255, 0, 0)
                    cv2.rectangle(img_cv, (x + j * int(w / len(raw_text)), y),
                                  (x + (j + 2) * int(w / len(raw_text)), y + h), color, 2)
                    cv2.putText(img_cv, two_digit, (x + j * int(w / len(raw_text)), y - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        else:
            text = raw_text.zfill(2)
            recognized.append(text)
            color = (0, 0, 255) if text in user_numbers else (255, 0, 0)
            cv2.rectangle(img_cv, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img_cv, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # 🖼️ Ausgabe als Bild
    result_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    result_pil = Image.fromarray(result_rgb)
    img_io = BytesIO()
    result_pil.save(img_io, 'JPEG')
    img_io.seek(0)

    # 📦 JSON-Daten
    json_data = json.dumps({'recognized': recognized})

    # Multipart-Antwort
    multipart = MIMEMultipart('mixed')
    multipart.attach(MIMEImage(img_io.read(), _subtype='jpeg', name='result.jpg'))
    multipart.attach(MIMEApplication(json_data, _subtype='json', name='data.json'))

    out = BytesIO()
    g = BytesGenerator(out, mangle_from_=False)
    g.flatten(multipart)

    return Response(out.getvalue(), content_type=f'multipart/mixed; boundary="{multipart.get_boundary()}"')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
