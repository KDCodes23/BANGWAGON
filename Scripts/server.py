from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import base64
import io
import datetime
from google import genai

app = Flask(__name__)
CORS(app)

# Your Gemini API key - replace with your actual API key
GEMINI_API_KEY = "AIzaSyDjxSP-BAwRjQWa0V8xgTo4e3uMtuibSyI"
client = genai.Client(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = "gemini-2.0-flash"

# Ontario license regex for basic validation
LICENSE_REGEX = re.compile(r'\b([A-Z]\d{4}[ -]?\d{5}[ -]?\d{5})\b')

def is_valid_canadian_license(license_number):
    clean = license_number.replace('-', '').replace(' ', '')
    return len(clean) == 14 and clean[0] in 'ABCDEFGHX'

def clean_ocr_text(text):
    return text.upper() \
        .replace('O', '0').replace('Q', '0') \
        .strip()

def calculate_age(dob_str):
    try:
        # Parse date in YYYY/MM/DD format
        year, month, day = map(int, dob_str.split('/'))
        dob = datetime.date(year, month, day)
        
        # Calculate age based on current date (2025)
        today = datetime.date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except Exception as e:
        print(f"Error calculating age: {str(e)}")
        return 0

def extract_license_info_with_gemini(image_base64):
    """Use Gemini to extract license information"""
    try:
        # Create the prompt for Gemini
        prompt = """
        Extract the following information from this driver's license image:
        - License Number (format usually like A1234-12345-12345)
        - Full Name
        - Date of Birth (in YYYY/MM/DD format)
        - Complete Address
        
        The person must be at least 16 years old to have a license.
        If multiple dates are found, choose the one that makes the person at least 16 years old, assuming the current year is 2025.
        
        Return the result in JSON format with these keys: "license_number", "name", "dob", "address".
        For any fields you cannot find, use "Not found" as the value.
        """
        
        # Call Gemini API with the image
        response = client.models.generate_content(
            model=model,
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": image_base64}}
                    ]
                }
            ]
        )
        
        # Extract JSON from the response
        import json
        try:
            # Try to parse the response text as JSON
            result = json.loads(response.text)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON from text
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                # Create default structure if no JSON found
                result = {
                    "name": "Not found",
                    "dob": "Not found",
                    "address": "Not found"
                }
        
        # Validate date of birth - ensure person is at least 16 years old
        if result.get("dob") and result.get("dob") != "Not found":
            age = calculate_age(result["dob"])
            if age < 16:
                result["dob"] = "Invalid DOB - age must be 16+"
        
        return result
    
    except Exception as e:
        import traceback
        print(f"Error with Gemini API: {str(e)}")
        print(traceback.format_exc())
        return {
            "name": "Error in extraction",
            "dob": "Not found",
            "address": "Not found"
        }

@app.route('/process-license', methods=['POST'])
def process_license():
    try:
        # Get JSON data and validate
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'success': False, 'error': 'No image data received'}), 400
            
        # Extract base64 image data
        image_data = data['image'].split(',')[1] if ',' in data['image'] else data['image']
        
        # Use Gemini Vision API to extract license information
        license_info = extract_license_info_with_gemini(image_data)
        
        # Validate license number format with regex if needed
        license_number = license_info.get('license_number', 'Not found')
        if license_number != 'Not found':
            # Try to clean and validate the license number
            clean_license = license_number.replace(' ', '').replace('-', '')
            if LICENSE_REGEX.search(clean_license):
                # Format it properly with dashes if it's valid
                if len(clean_license) == 15:  # Adjust based on expected format
                    license_number = f"{clean_license[0:5]}-{clean_license[5:10]}-{clean_license[10:15]}"
        
        return jsonify({
            'success': True,
            'license_number': license_number,
            'full_name': license_info.get('name', 'Not found'),
            'dob': license_info.get('dob', 'Not found'),
            'address': license_info.get('address', 'Not found')
        })
        
    except Exception as e:
        import traceback
        print(f"Error processing license: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/test', methods=['GET'])
def test_route():
    return jsonify({'status': 'Server is running'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)