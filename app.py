import pytesseract
from flask import Flask, request, send_file
from flask_cors import CORS
from pytesseract import Output
import cv2
import numpy as np
import tempfile

app = Flask(__name__)
CORS(app)

@app.route('/check_lotto', methods=['POST'])
def check_lotto():
    if 'image' not in request.files or 'numbers' not in request.form:
        return 'Bild oder Zahlen fehlen', 400

    file = request.files['image']
    numbers_raw = request.form['numbers']
    try:
        drawn_numbers = set(map(int, numbers_raw.replace(',', ' ').split()))
    except ValueError:
        return 'Ungültige Zahlen', 400

    npimg = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    data = pytesseract.image_to_data(img, config='--psm 6 outputbase digits', output_type=Output.DICT)

    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        if text.isdigit():
            zahl = int(text)
            if zahl in drawn_numbers:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                center = (x + w // 2, y + h // 2)
                radius = max(w, h) // 2 + 5
                cv2.circle(img, center, radius, (0, 0, 255), 2)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    cv2.imwrite(tmp.name, img)
    tmp.close()
    return send_file(tmp.name, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
