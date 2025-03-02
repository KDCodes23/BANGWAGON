from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import cv2
import numpy as np
import re
from pyzbar.pyzbar import decode
import cv2
import numpy as np
import re
from pyzbar.pyzbar import decode
from google.cloud import vision

app = Flask(__name__)
CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}})


# Initialize Google Vision client
client = vision.ImageAnnotatorClient()

# Ontario Driver's License Regex Patterns
LICENSE_REGEX = re.compile(r"\b([A-Z]\d{4}[ -]?\d{5}[ -]?\d{5})\b")
NAME_REGEX = re.compile(r"Surname/Nom:\s*([A-Z]+)\s*\nGiven Name\(s\)/Prénom\(s\):\s*([A-Z]+)")
DOB_REGEX = re.compile(r"\b(\d{4}/\d{2}/\d{2})\b")
ADDRESS_REGEX = re.compile(r"Address/Adresse:\s*(.+?),\s*([A-Z]+),\s*([A-Z]{2})\s*([A-Z0-9\s]+)")

def preprocess_image(image_bytes):
    """ Enhance image quality for better OCR recognition """
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Image decoding failed. Ensure valid image data is provided.")

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding
    processed = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Convert back to bytes
    _, processed_bytes = cv2.imencode(".jpg", processed)
    return processed_bytes.tobytes()
# Ontario Driver's License Regex Patterns
LICENSE_REGEX = re.compile(r"\b([A-Z]\d{4}[ -]?\d{5}[ -]?\d{5})\b")
NAME_REGEX = re.compile(r"Surname/Nom:\s*([A-Z]+)\s*\nGiven Name\(s\)/Prénom\(s\):\s*([A-Z]+)")
DOB_REGEX = re.compile(r"\b(\d{4}/\d{2}/\d{2})\b")
ADDRESS_REGEX = re.compile(r"Address/Adresse:\s*(.+?),\s*([A-Z]+),\s*([A-Z]{2})\s*([A-Z0-9\s]+)")

def preprocess_image(image_bytes):
    """ Enhance image quality for better OCR recognition """
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding
    processed = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Save and check processed image (for debugging)
    cv2.imwrite("processed_license.jpg", processed)

    # Convert back to bytes
    _, processed_bytes = cv2.imencode(".jpg", processed)
    return processed_bytes.tobytes()

def extract_text_ocr(image_bytes):
    """ Extract text from image using Google OCR """
    vision_image = vision.Image(content=image_bytes)
    response = client.text_detection(image=vision_image)

    if response.error.message:
        print("❌ Google Vision API Error:", response.error.message)
        return None

    text = response.text_annotations[0].description if response.text_annotations else ""
    print("🔍 OCR Extracted Text:\n", text)
    return text

def decode_barcode(image_bytes):
    """ Extract barcode data (PDF417) from the image """
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    barcodes = decode(image)

    extracted_data = {}

    for barcode in barcodes:
        barcode_data = barcode.data.decode("utf-8")
        print("🔍 Decoded Barcode Data:\n", barcode_data)

        # Example: Parse barcode structured data
        lines = barcode_data.split("\n")
        extracted_data["license_number"] = lines[0].strip()
        extracted_data["full_name"] = f"{lines[1]} {lines[2]}" if len(lines) > 2 else None
        extracted_data["dob"] = lines[3] if len(lines) > 3 else None
        extracted_data["address"] = lines[4] if len(lines) > 4 else None

    return extracted_data

@app.route("/process-license", methods=["POST"])
def extract_text_ocr(image_bytes):
    """ Extract text from image using Google OCR """
    vision_image = vision.Image(content=image_bytes)
    response = client.text_detection(image=vision_image)

    if response.error.message:
        print("❌ Google Vision API Error:", response.error.message)
        return None

    text = response.text_annotations[0].description if response.text_annotations else ""
    print("🔍 OCR Extracted Text:\n", text)
    return text

def decode_barcode(image_bytes):
    """ Extract barcode data (PDF417) from the image """
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    barcodes = decode(image)

    extracted_data = {}

    for barcode in barcodes:
        barcode_data = barcode.data.decode("utf-8")
        print("🔍 Decoded Barcode Data:\n", barcode_data)

        # Example: Parse barcode structured data
        lines = barcode_data.split("\n")
        extracted_data["license_number"] = lines[0].strip()
        extracted_data["full_name"] = f"{lines[1]} {lines[2]}" if len(lines) > 2 else None
        extracted_data["dob"] = lines[3] if len(lines) > 3 else None
        extracted_data["address"] = lines[4] if len(lines) > 4 else None

    return extracted_data

@app.route("/process-license", methods=["POST"])
def process_license():
    try:
        # Get JSON data and validate
        data = request.get_json()
        if not data or "image" not in data:
            return jsonify({"success": False, "error": "No image data received"}), 400

        if not data or "image" not in data:
            return jsonify({"success": False, "error": "No image data received"}), 400

        # Extract base64 image data
        image_data = data["image"].split(",")[1] if "," in data["image"] else data["image"]
        image_data = data["image"].split(",")[1] if "," in data["image"] else data["image"]
        image_bytes = base64.b64decode(image_data)

        # Process image for better OCR
        processed_image = preprocess_image(image_bytes)

        # Try barcode first
        barcode_info = decode_barcode(image_bytes)
        if barcode_info:
            return jsonify({"success": True, **barcode_info})

        # Fallback to OCR if barcode fails
        text = extract_text_ocr(processed_image)
        if not text:
            return jsonify({"success": False, "error": "Could not extract text"}), 400

        # Extract data using regex
        license_match = LICENSE_REGEX.search(text)
        name_match = NAME_REGEX.search(text)
        dob_match = DOB_REGEX.search(text)
        address_match = ADDRESS_REGEX.search(text)


        # Process image for better OCR
        processed_image = preprocess_image(image_bytes)

        # Try barcode first
        barcode_info = decode_barcode(image_bytes)
        if barcode_info:
            return jsonify({"success": True, **barcode_info})

        # Fallback to OCR if barcode fails
        text = extract_text_ocr(processed_image)
        if not text:
            return jsonify({"success": False, "error": "Could not extract text"}), 400

        # Extract data using regex
        license_match = LICENSE_REGEX.search(text)
        name_match = NAME_REGEX.search(text)
        dob_match = DOB_REGEX.search(text)
        address_match = ADDRESS_REGEX.search(text)

        license_number = license_match.group(1) if license_match else None
        full_name = f"{name_match.group(1)} {name_match.group(2)}" if name_match else None
        dob = dob_match.group(1) if dob_match else None


        if address_match:
            street = address_match.group(1)
            street = address_match.group(1)
            city = address_match.group(2)
            province = address_match.group(3)
            postal_code = address_match.group(4)
            postal_code = address_match.group(4)
            address = f"{street}, {city}, {province} {postal_code}"
        else:
            address = None

        return jsonify({
            "success": True,
            "license_number": license_number,
            "full_name": full_name,
            "dob": dob,
            "address": address,
            "success": True,
            "license_number": license_number,
            "full_name": full_name,
            "dob": dob,
            "address": address,
        })


    except Exception as e:
        import traceback
        print(f"❌ Error processing license: {str(e)}")
        print(f"❌ Error processing license: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/test", methods=["GET"])
@app.route("/test", methods=["GET"])
def test_route():
    return jsonify({"status": "Server is running"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    return jsonify({"status": "Server is running"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)