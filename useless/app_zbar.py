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
    return pd.DataFrame(columns=["Barcode", "Name", 'Expiration Date', "Comment"])

# Function to save data to CSV
def save_data(df,barcode_result,name,expiration_date = None,comment=None):
    df = load_data()
    new_entry = pd.DataFrame([[barcode_result, name, expiration_date, comment]],
                             columns=["Barcode", "Name", 'Expiration Date', "Comment"])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    st.success('save successful')

def update_data(df):
    df.to_csv(CSV_FILE, index=False)

def remove_data(df,barcode_result):
    df = load_data()
    df_new = df[df['Barcode'] != barcode_result]
    df_new.to_csv(CSV_FILE, index=False)
    st.warning('remove successful')

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

# Use session state to persist barcode across reruns
if "barcode_result" not in st.session_state:
    st.session_state["barcode_result"] = None

if image:
    decoded_objects = process_image(image)
    if decoded_objects:
        barcode_result = decoded_objects[0].data.decode("utf-8")
        st.session_state["barcode_result"] = barcode_result
        st.success(f" Scanned Barcode: **{barcode_result}**")
    else:
        st.error(" No barcode detected! Try again with better lighting.")

# If a barcode was scanned, allow user input
if st.session_state["barcode_result"]:
    df = load_data()
    barcode_result = st.session_state["barcode_result"]  # Retrieve barcode
    st.subheader(" Add Inventory")
    if st.button("Add Inventory"):
        name = st.text_input("Enter Item Name")
        expiration_date = st.text_area("Expiration Date (Optional)")
        comment = st.text_area("Enter Comments (Optional)")
        if st.button("Confirm Add Inventory"):
            if name.strip():
                save_data(barcode_result, name, expiration_date, comment)

            else:
                st.error("Please enter a valid item name.")

    st.subheader("Remove Inventory")
    if st.button("Remove Inventory"):
        st.warning("Are you sure you want to remove this item?")
        if st.button("Confirm Removal"):
            remove_data(barcode_result)


# Load existing scanned data
df = load_data()
st.write("### Edit Scanned Data")

# **Editable Data Table**
edited_df = st.data_editor(
    df, #input pandas data
    column_config={
        "Expiration Date": st.column_config.DateColumn(
        'Expiration Date',
            format="DD.MM.YYYY",
            step =1,),},
        num_rows="dynamic")

# **Save Changes Button**
if st.button("Save Changes"):
    update_data(edited_df)
    st.success("Changes saved successfully!")
    #st.experimental_rerun()


# **Provide CSV Download Button**
csv_data = df.to_csv(index=False).encode("utf-8")
st.download_button(" Download CSV", csv_data, "scanned_data.csv", "text/csv")
