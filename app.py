from flask import Flask, request, Response
from flask_cors import CORS
import pytesseract
import cv2
import numpy as np
from PIL import Image
from pytesseract import Output
import json
from io import BytesIO
from email.generator import BytesGenerator
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return 'Lotto Checker API läuft!'

@app.route('/check_lotto', methods=['POST'])
def check_lotto():
    if 'image' not in request.files or 'numbers' not in request.form:
        return {'error': 'Bild oder Zahlen fehlen'}, 400

    image_file = request.files['image']
    user_numbers = [num.strip() for num in request.form['numbers'].split(',') if num.strip().isdigit()]

    # Bild vorbereiten
    img_pil = Image.open(image_file).convert('RGB')
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    # OCR-Konfiguration
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
    data = pytesseract.image_to_data(img_cv, config=custom_config, output_type=Output.DICT)

    recognized = []
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        if text.isdigit():
            # Lange Zahlen in Zweiergruppen aufteilen
            detected_numbers = [text[j:j+2] for j in range(0, len(text), 2)] if len(text) > 2 else [text]
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])

            for num in detected_numbers:
                recognized.append(num)
                color = (0, 0, 255) if num in user_numbers else (200, 200, 200)
                cv2.rectangle(img_cv, (x, y), (x + w, y + h), color, 2)
                cv2.putText(img_cv, num, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # Bild in Bytes konvertieren
    result_image = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    pil_result = Image.fromarray(result_image)
    img_io = BytesIO()
    pil_result.save(img_io, 'JPEG')
    img_io.seek(0)

    # JSON-Daten vorbereiten
    json_data = json.dumps({'recognized': recognized})

    # Multipart-Antwort bauen
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
