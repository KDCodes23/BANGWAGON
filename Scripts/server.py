import cv2
import numpy as np
import time
import base64
from google.cloud import vision

# Initialize the Google Vision client.
client = vision.ImageAnnotatorClient()

def get_ocr_annotations(image_bytes):
    """
    Use the Google Vision API to get OCR annotations from image bytes.
    Returns a list of annotations (skipping the first element which is full text).
    """
    vision_image = vision.Image(content=image_bytes)
    response = client.text_detection(image=vision_image)
    if response.error.message:
        print("Google Vision API error:", response.error.message)
        return []
    if not response.text_annotations:
        return []
    # The first element is the complete OCR text; subsequent elements are individual text elements with bounding boxes.
    return response.text_annotations[1:]

def draw_bounding_boxes(frame, annotations):
    """
    Draws bounding boxes and text labels on the frame for each OCR annotation.
    """
    for annotation in annotations:
        vertices = [(vertex.x, vertex.y) for vertex in annotation.bounding_poly.vertices]
        pts = np.array(vertices, np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
        # Put the OCR'd text near the top-left corner of the bounding box.
        if annotation.description:
            cv2.putText(frame, annotation.description, (vertices[0][0], vertices[0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return frame

def main():
    # Open the default webcam.
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return

    # Update OCR every update_interval seconds.
    update_interval = 3  # seconds
    last_update = 0
    annotations = []  # Current OCR annotations

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break

        current_time = time.time()
        # Every update_interval seconds, send the current frame to Google Vision for OCR.
        if current_time - last_update > update_interval:
            ret2, buffer = cv2.imencode('.jpg', frame)
            if ret2:
                image_bytes = buffer.tobytes()
                try:
                    annotations = get_ocr_annotations(image_bytes)
                    print("OCR update: found", len(annotations), "text elements.")
                except Exception as e:
                    print("Error during OCR:", e)
            else:
                print("Error encoding frame to JPEG.")
            last_update = current_time

        # Draw bounding boxes on the current frame using the last OCR result.
        frame_with_boxes = draw_bounding_boxes(frame.copy(), annotations)

        cv2.imshow("Live Feed with Google Vision OCR", frame_with_boxes)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
