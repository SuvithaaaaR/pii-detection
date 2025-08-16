from flask import Flask, request, jsonify, send_from_directory
from ocr import extract_text_from_file
from pii_detection import detect_pii
from rules_engine import check_necessity
from redaction import redact_pii
from flask_cors import CORS
import threading
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def serve_frontend():
    return send_from_directory(os.path.join(app.root_path, '../ui'), 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(os.path.join(app.root_path, '../ui'), path)

def detect_pii_background(text, pii_list_holder):
    pii_list_holder.append(detect_pii(text))

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    service_type = request.form.get('service_type', 'default')
    text = extract_text_from_file(file)
    pii_list_holder = []
    thread = threading.Thread(target=detect_pii_background, args=(text, pii_list_holder))
    thread.start()
    thread.join()  # For demo: wait for background to finish (remove for true async)
    pii_list = pii_list_holder[0] if pii_list_holder else []
    necessity = check_necessity(pii_list, service_type)
    print("Returning response:", {'pii': pii_list, 'necessity': necessity})
    return jsonify({'pii': pii_list, 'necessity': necessity})

@app.route('/redact', methods=['POST'])
def redact_file():
    file = request.files['file']
    pii_to_redact = request.form.getlist('pii')
    redacted_file = redact_pii(file, pii_to_redact)
    # For demo, just return a success message
    return jsonify({'status': 'redacted', 'pii_redacted': pii_to_redact})

@app.route('/download-masked', methods=['POST'])
def download_masked():
    file = request.files['file']
    text = extract_text_from_file(file)
    pii_list = detect_pii(text)
    masked_text = text
    for pii in pii_list:
        masked_text = masked_text.replace(pii['value'], pii['masked'])
    # Return as downloadable text file
    return (masked_text, 200, {
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Disposition': 'attachment; filename="masked.txt"'
    })

if __name__ == '__main__':
    app.run(debug=True)
