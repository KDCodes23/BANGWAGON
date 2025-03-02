from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import cv2
import numpy as np
import re
from pyzbar.pyzbar import decode
from google.cloud import vision
import os
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize the Google Vision API client
client = vision.ImageAnnotatorClient()

# Regular expressions for license and data extraction
LICENSE_REGEX = re.compile(r"\b([A-Z]\d{4}[ -]?\d{5}[ -]?\d{5})\b")
NAME_REGEX = re.compile(r"(?:Surname|Nom)[\s:]*([A-Z\s]+)[\s\n]+(?:Given Name|Prénom)[\s:\(\)]*([A-Z\s]+)")
DOB_REGEX = re.compile(r"(?:Date of Birth|Date de naissance)[\s:]*(\d{4}/\d{2}/\d{2})")
ADDRESS_REGEX = re.compile(r"(?:Address|Adresse)[\s:]*([^,]+),\s*([A-Z\s]+),\s*([A-Z]{2})[\s,]*([A-Z0-9]{6}|[A-Z][0-9][A-Z]\s?[0-9][A-Z][0-9])")

# Function to preprocess image
def preprocess_image(image_bytes):
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Image decoding failed.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    processed = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 11, 2)
    return processed

# Function to detect license number from image using pyzbar
def detect_license_number(image_bytes):
    processed_image = preprocess_image(image_bytes)
    decoded_objects = decode(processed_image)

    license_number = None
    for obj in decoded_objects:
        text = obj.data.decode('utf-8')
        match = LICENSE_REGEX.search(text)
        if match:
            license_number = match.group(0)
            break

    return license_number

# Function to extract text from image using Google Vision API
def extract_text_from_image(image_bytes):
    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)

    if response.error.message:
        raise Exception(f'Error occurred: {response.error.message}')

    text = response.text_annotations[0].description
    return text

# Function to extract name, date of birth, and address from extracted text
def extract_data_from_text(text):
    name_match = NAME_REGEX.search(text)
    dob_match = DOB_REGEX.search(text)
    address_match = ADDRESS_REGEX.search(text)

    name = f"{name_match.group(1)} {name_match.group(2)}" if name_match else None
    dob = dob_match.group(1) if dob_match else None
    address = f"{address_match.group(1)}, {address_match.group(2)}, {address_match.group(3)} {address_match.group(4)}" if address_match else None

    return name, dob, address

@app.route('/process-license', methods=['POST'])
def process_license():
    try:
        data = request.get_json()
        image_data = data['image']
        image_bytes = base64.b64decode(image_data.split(',')[1])

        # Detect the license number
        license_number = detect_license_number(image_bytes)

        # Extract text and further data (name, dob, address)
        text = extract_text_from_image(image_bytes)
        name, dob, address = extract_data_from_text(text)

        # Respond with the data found
        response_data = {
            'success': True,
            'license_number': license_number,
            'full_name': name,
            'dob': dob,
            'address': address
        }
        return jsonify(response_data)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
