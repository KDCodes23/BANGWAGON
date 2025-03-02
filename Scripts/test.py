from BANGWAGON.Scripts.license import DriverInfo
import cv2
import easyocr
import numpy as np
import re
import json


# Initialize EasyOCR Reader
reader = easyocr.Reader(['en'], gpu=True)  # Enable GPU if available

# Start webcam capture
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Error: Could not open webcam.")
    exit()

print("\n📷 Live webcam feed started. Hold the driver's license steady in front of the camera.")
print("🔍 Extracting text in real-time... Press 'q' to quit.\n")

license_data = {
    "License Number": None,
    "Name": None,
    "DOB": None,
    "Address": None
}

# Define regex patterns for key details
license_number_pattern = r"\b[A-Z0-9]{5,15}\b"  # Modify based on region's format
dob_pattern = r"\b(\d{2}/\d{2}/\d{4})\b"  # Format: MM/DD/YYYY
address_keywords = ["Street", "Road", "Avenue", "Lane", "City", "State", "Zip", "Block"]  # Modify based on region

# Load OpenCV EAST text detector for improved speed
net = cv2.dnn.readNet("frozen_east_text_detection.pb")

def detect_text_regions(frame):
    """ Detect text regions using OpenCV EAST model """
    H, W = frame.shape[:2]
    newW, newH = (320, 320)  # Resize for EAST model
    rW, rH = W / newW, H / newH

    blob = cv2.dnn.blobFromImage(frame, 1.0, (newW, newH), (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net.setInput(blob)

    scores, geometry = net.forward(["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"])
    rects = []
    
    for y in range(scores.shape[2]):
        for x in range(scores.shape[3]):
            if scores[0, 0, y, x] > 0.5:  # Confidence threshold
                offsetX, offsetY = x * 4, y * 4
                angle = geometry[0, 4, y, x]
                cos, sin = np.cos(angle), np.sin(angle)
                h, w = geometry[0, 0, y, x] + geometry[0, 2, y, x], geometry[0, 1, y, x] + geometry[0, 3, y, x]
                endX, endY = int(offsetX + (cos * w) + (sin * h)), int(offsetY - (sin * w) + (cos * h))
                startX, startY = int(endX - w), int(endY - h)
                
                rects.append((startX * rW, startY * rH, endX * rW, endY * rH))
    
    return rects

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to capture frame.")
        break

    # Convert to grayscale and enhance contrast
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Detect text regions
    text_regions = detect_text_regions(frame)

    # Extract and recognize text only from detected regions
    for (startX, startY, endX, endY) in text_regions:
        roi = gray[int(startY):int(endY), int(startX):int(endX)]
        results = reader.readtext(roi)

        for (bbox, text, prob) in results:
            if prob < 0.5:  # Skip low-confidence results
                continue

            # Draw bounding boxes
            cv2.rectangle(frame, (int(startX), int(startY)), (int(endX), int(endY)), (0, 255, 0), 2)
            cv2.putText(frame, text, (int(startX), int(startY) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Process extracted text
            if re.match(license_number_pattern, text) and license_data["License Number"] is None:
                license_data["License Number"] = text
            if re.search(dob_pattern, text):
                license_data["DOB"] = re.search(dob_pattern, text).group(1)
            if any(keyword in text for keyword in address_keywords):
                license_data["Address"] = text
            if license_data["Name"] is None and text.isalpha() and len(text) > 3:
                license_data["Name"] = text

    # Show live video with detected text
    cv2.imshow("Live OCR - Driver's License Scanner (Press 'q' to Quit)", frame)

    # Stop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

# Print extracted license details
print("\n✅ Extracted License Information:")
for key, value in license_data.items():
    print(f"{key}: {value}")

# Save extracted details to a JSON file
with open("license_details.json", "w") as json_file:
    json.dump(license_data, json_file, indent=4)

object = DriverInfo(
    license_data["License Number"],
    license_data["Name"],
    license_data["DOB"],
    license_data["Address"]
)

object.convert_to_json()


print("\n💾 License details saved in 'license_details.json'")
