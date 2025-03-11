import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO

# Load YOLOv8 Barcode/QR model
model = YOLO("yolov8n.pt")  # Make sure the model file exists in the working directory


# Function to process frames from webcam
def detect_barcode(frame):
    results = model(frame)  # Run YOLOv8 on the frame

    barcode_results = set()  # Use a set to store unique barcode detections
    for result in results:
        if result.boxes is not None:
            for box in result.boxes.data.tolist():  # Extract bounding box info
                x1, y1, x2, y2, confidence, class_id = box
                if confidence > 0.5:  # Filter low-confidence detections
                    barcode_results.add(f"Barcode detected with confidence {confidence:.2f}")

    return list(barcode_results) if barcode_results else ["No barcode detected"]


# Streamlit UI
st.title("Real-Time YOLO Barcode & QR Scanner")

# Start webcam
cap = cv2.VideoCapture(0)  # Use default webcam

# Run the webcam loop in Streamlit
if st.button("Start Camera"):
    st.write("Camera is running... Press Stop to exit.")

    # Display camera feed
    FRAME_WINDOW = st.image([])

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            st.error("Failed to capture frame. Check your webcam.")
            break

        # Detect barcodes/QR codes
        barcode_result = detect_barcode(frame)

        # Convert frame to RGB for Streamlit
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        FRAME_WINDOW.image(frame, channels="RGB")

        # Display detected barcode result (only once)
        if barcode_result and barcode_result[0] != "No barcode detected":
            print(barcode_result[0])
            st.write(barcode_result[0])
            st.success(barcode_result[0])

# Stop the camera
if st.button("Stop Camera"):
    cap.release()
    st.warning("Camera stopped.")
