from BANGWAGON.Scripts.license import DriverInfo
import cv2
import easyocr
import numpy as np
import re
import json


# Initialize EasyOCR Reader
reader = easyocr.Reader(['en'])

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

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to capture frame.")
        break

    # Convert to grayscale for better OCR accuracy
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding to enhance text visibility
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Perform OCR on the live frame
    results = reader.readtext(gray)

    # Draw bounding boxes around detected text
    for (bbox, text, prob) in results:
        top_left, top_right, bottom_right, bottom_left = bbox
        top_left = tuple(map(int, top_left))
        bottom_right = tuple(map(int, bottom_right))

        # Draw rectangle around detected text
        cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

        # Put detected text above the bounding box
        cv2.putText(frame, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Process extracted text to filter key details
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


print("\n💾 License details saved in 'license_details.json'")
