# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS  # Add this
import re
import base64
import io
from PIL import Image
import pytesseract

app = Flask(__name__)
CORS(app)  # Enable CORS

app = Flask(__name__)

# Ontario license patterns
LICENSE_REGEX = re.compile(r'\b([A-Z]\d{4}[ -]?\d{5}[ -]?\d{5})\b')
NAME_REGEX = re.compile(r'(?m)^.*\d{2}[A-Z]+.*\n([A-Z]+)\n([A-Z]+)')
DOB_REGEX = re.compile(r'\b(\d{4}/\d{2}/\d{2})\b')
ADDRESS_REGEX = re.compile(r'(\d+[-\\w]+)\n([A-Z]+),([A-Z]{2}),([A-Z0-9]{6})')
POSTAL_CODE_REGEX = re.compile(r'([A-Z]\d[A-Z])\s?(\d[A-Z]\d)')

def clean_ocr_text(text):
    return text.upper() \
        .replace('O', '0').replace('Q', '0') \
        .replace(' ', '') \
        .replace('\n', ' ') \
        .strip()

def is_valid_canadian_license(license_number):
    clean = license_number.replace('-', '').replace(' ', '')
    return len(clean) == 14 and clean[0] in 'ABCDEFGHX'

@app.route('/process-license', methods=['POST'])
def process_license():
    try:
        data = request.json
        image_data = data['image'].split(',')[1]  # Remove data URL prefix
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))
        
        # OCR processing
        text = pytesseract.image_to_string(image)
        cleaned_text = clean_ocr_text(text)
        
        # Extract data
        license_match = LICENSE_REGEX.search(cleaned_text)
        license_number = license_match.group(1) if license_match else None
        
        name_match = NAME_REGEX.search(cleaned_text)
        full_name = f"{name_match.group(1)} {name_match.group(2)}" if name_match else None
        
        dob_match = DOB_REGEX.search(cleaned_text)
        dob = dob_match.group(1) if dob_match else None
        
        address_match = ADDRESS_REGEX.search(cleaned_text)
        if address_match:
            street = re.sub(r'(?<=\d)(?=[A-Z])', ' ', address_match.group(1))
            city = address_match.group(2)
            province = address_match.group(3)
            postal_code = POSTAL_CODE_REGEX.sub(r'\1 \2', address_match.group(4))
            address = f"{street}, {city}, {province} {postal_code}"
        else:
            address = None

        return jsonify({
            'success': True,
            'license_number': license_number,
            'full_name': full_name,
            'dob': dob,
            'address': address
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })
@app.route('/process-license', methods=['POST'])
def process_license():
    try:
        data = request.get_json()  # Changed from request.json
        if not data or 'image' not in data:
            return jsonify({'success': False, 'error': 'No image data received'}), 400
            
        # Extract base64 image data
        image_data = data['image'].split(',')[1] if ',' in data['image'] else data['image']
        
        # Decode image
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))
        
        # OCR processing
        text = pytesseract.image_to_string(image)
        cleaned_text = clean_ocr_text(text)
        
        # ... (rest of your existing processing code) ...

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 