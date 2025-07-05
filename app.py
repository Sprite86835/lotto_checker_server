from flask import Flask, request, send_file
from flask_cors import CORS
import pytesseract
import cv2
import numpy as np
from PIL import Image
from pytesseract import Output
from io import BytesIO

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
    user_numbers = [num.strip() for num in request.form['numbers'].split(',') if num.strip().isdigit()]

    # Bild vorbereiten
    img_pil = Image.open(image_file).convert('RGB')
    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    # OCR durchführen
    data = pytesseract.image_to_data(img_cv, config='--psm 6 outputbase digits', output_type=Output.DICT)

    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        if text.isdigit():
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            color = (0, 0, 255) if text in user_numbers else (255, 0, 0)
            cv2.rectangle(img_cv, (x, y), (x + w, y + h), color, 2)

    # Bild in Bytes konvertieren
    result_image = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    pil_result = Image.fromarray(result_image)
    img_io = BytesIO()
    pil_result.save(img_io, 'JPEG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/jpeg')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
