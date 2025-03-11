import streamlit as st
import cv2
import numpy as np
import easyocr
import tempfile
import os
import pandas as pd



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

reader = easyocr.Reader(['en'])
# function to process image and scan barcode
def process_image(uploaded_file):
    #save uploaded file to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_path = temp_file.name

    #read the image using OpenCV
    image = cv2.imread(temp_path)

    #convert image using grayscale for better detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # apply adaptive thresholding to enhance barcode visibility
    processed = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    #use easy reader
    results = reader.readtext(processed, allowlist ='0123456789')

    barcode_result = None

    # Extract detected barcode text
    if results and len(results) > 0:
        barcode_result = results[0][-2]# Extracts text from OCR output
    else:
        barcode_result = "No barcode detected"

    # Delete the temporary file
    os.remove(temp_path)
    return barcode_result

# Streamlit UI
st.title(" Barcode Scanner & Inventory Logger")
st.write("Scan a barcode, enter item details, and save the data.")

# Camera input for scanning
image = st.camera_input(" Scan Barcode or QR Code")

barcode_result = None
if image:
    decoded_objects = process_image(image)
    if decoded_objects:
        st.write("Decoded easyocr Output:", decoded_objects)
        barcode_result = decoded_objects[0]
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
