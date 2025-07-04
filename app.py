from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import pytesseract
from pytesseract import Output
import io

app = Flask(__name__)
CORS(app)

@app.route('/check_lotto', methods=['POST'])
def check_lotto():
    file = request.files.get('image')
    numbers_raw = request.form.get('numbers', '')

    if not file or not numbers_raw:
        return jsonify({"error": "Missing image or numbers"}), 400

    try:
        numbers = list(map(int, numbers_raw.split(',')))
    except ValueError:
        return jsonify({"error": "Invalid number format. Use comma-separated integers."}), 400

    # Bild lesen und vorbereiten
    file_bytes = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY_INV)

    # OCR mit nur Ziffern
    config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
    data = pytesseract.image_to_data(thresh, config=config, output_type=Output.DICT)

    detected_numbers = []
    matched_numbers = []

    for i, text in enumerate(data['text']):
        text = text.strip()
        if text.isdigit():
            num = int(text)
            detected_numbers.append(num)

            if num in numbers:
                matched_numbers.append(num)
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Rot

    # Codiertes Bild
    _, encoded_img = cv2.imencode('.jpg', img)
    image_stream = io.BytesIO(encoded_img.tobytes())

    # Antwort: JSON mit Treffer + Bild
    response_data = {
        "numbers_from_ticket": sorted(list(set(detected_numbers))),
        "matched_numbers": sorted(list(set(matched_numbers)))
    }

    # Multipart: JSON + Bild
    from flask import Response
    import json
    boundary = 'MULTIPART_BOUNDARY'

    multipart_body = (
        f"--{boundary}\r\n"
        f"Content-Type: application/json\r\n\r\n"
        f"{json.dumps(response_data)}\r\n"
        f"--{boundary}\r\n"
        f"Content-Type: image/jpeg\r\n"
        f"Content-Disposition: attachment; filename=result.jpg\r\n\r\n"
    ).encode('utf-8') + image_stream.read() + f"\r\n--{boundary}--".encode('utf-8')

    return Response(
        multipart_body,
        mimetype=f'multipart/mixed; boundary={boundary}'
    )
