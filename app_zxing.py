import streamlit as st
import pandas as pd
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import os

# CSV file path
CSV_FILE = "scanned_data.csv"

# Function to load existing data or create a new file
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=["Barcode", "Name", "Comment"])

# Function to save data to CSV
def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# Function to process image and scan barcode
def process_image(image):
    image_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
    frame = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
    decoded_objects = decode(thresh)
    return decoded_objects

# Streamlit UI
st.title(" Barcode Scanner & Inventory Logger")
st.write("Scan a barcode, enter item details, and save the data.")

# Camera input for scanning
image = st.camera_input(" Scan Barcode or QR Code")

barcode_result = None

if image:
    decoded_objects = process_image(image)
    if decoded_objects:
        barcode_result = decoded_objects[0].data.decode("utf-8")
        st.success(f" Scanned Barcode: **{barcode_result}**")
    else:
        st.error(" No barcode detected! Try again with better lighting.")

# If a barcode was scanned, allow user input
if barcode_result:
    name = st.text_input(" Enter Item Name", "")
    comment = st.text_area(" Enter Comments (Optional)", "")

    if st.button("💾 Save Data"):
        df = load_data()
        new_entry = pd.DataFrame([[barcode_result, name, comment]], columns=["Barcode", "Name", "Comment"])
        df = pd.concat([df, new_entry], ignore_index=True)
        save_data(df)
        st.success(" Data saved successfully!")
        st.experimental_rerun()

# Load existing scanned data
df = load_data()
st.write("### Edit Scanned Data")

# **Editable Data Table**
edited_df = st.data_editor(df, num_rows="dynamic")

# **Save Changes Button**
if st.button("Save Changes"):
    save_data(edited_df)
    st.success("Changes saved successfully!")
    st.experimental_rerun()


# **Provide CSV Download Button**
csv_data = df.to_csv(index=False).encode("utf-8")
st.download_button(" Download CSV", csv_data, "scanned_data.csv", "text/csv")
