import cv2

# Open camera
cap = cv2.VideoCapture(0)  # 0 for default webcam

# Set resolution (adjust as needed)
cap.set(3, 1920)  # Width
cap.set(4, 1080)  # Height

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Show frame
    cv2.imshow("Driver's License Scanner", frame)
    
    # Capture on 's' key press
    if cv2.waitKey(1) & 0xFF == ord('s'):
        cv2.imwrite("license.jpg", frame)
        print("Image captured!")
        break

# Release resources
cap.release()
cv2.destroyAllWindows()