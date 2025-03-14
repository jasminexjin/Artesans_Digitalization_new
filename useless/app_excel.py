import streamlit as st
import pandas as pd
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import os

# Excel file path
EXCEL_FILE = "Book3.xlsx"


# Function to load existing data or create a new Excel file
def load_data():
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE, engine="openpyxl")
    else:
        df = pd.DataFrame(columns=["Barcode", "Name", "Expiration Date", "Comment"])
        df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")
        return df


# Function to save new inventory data to Excel
def save_data(barcode_result, name, expiration_date=None, comment=None):
    df = load_data()

    # Prevent duplicate barcode entries
    if barcode_result in df["Barcode"].astype(str).values:
        st.warning("This item is already in the inventory!")
        return
    df["Expiration Date"] = pd.to_datetime(df["Expiration Date"], errors='coerce')

    new_entry = pd.DataFrame([[barcode_result, name, expiration_date, comment]],
                             columns=["Barcode", "Name", "Expiration Date", "Comment"])

    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")
    st.success("Inventory item added successfully!")
    st.rerun()


# Function to remove data from Excel
def remove_data(barcode_result):
    df = load_data()

    # Check if the barcode exists before attempting to remove it
    if barcode_result not in df["Barcode"].astype(str).values:
        st.warning("This item does not exist in the inventory!")
        return
    df = df[df["Barcode"].astype(str) != barcode_result]
    df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")
    st.warning("Inventory item removed successfully!")
    st.rerun()


# Function to process image and scan barcode
def process_image(image):
    image_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
    frame = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
    decoded_objects = decode(thresh)
    return decoded_objects


# Streamlit UI
st.title("Barcode Scanner & Inventory Logger (Excel Integration)")
st.write("Scan a barcode, enter item details, and manage inventory in Excel.")

# Camera input for scanning
image = st.camera_input("Scan Barcode or QR Code")

# Use session state to persist barcode across reruns
if "barcode_result" not in st.session_state:
    st.session_state["barcode_result"] = None

if image:
    decoded_objects = process_image(image)
    if decoded_objects:
        barcode_result = decoded_objects[0].data.decode("utf-8")
        st.session_state["barcode_result"] = barcode_result
        st.success(f"Scanned Barcode: {barcode_result}")
    else:
        st.error("No barcode detected! Try again with better lighting.")

# If a barcode was scanned, allow user input
if st.session_state["barcode_result"]:
    barcode_result = st.session_state["barcode_result"]  # Retrieve barcode
    df = load_data()

    st.subheader("Add Inventory")

    # Inputs outside button logic so they persist
    name = st.text_input("Enter Item Name")
    expiration_date = st.text_input("Expiration Date (Optional)")
    comment = st.text_area("Enter Comments (Optional)")

    if st.button("Confirm Add Inventory"):
        if name.strip():
            save_data(barcode_result, name, expiration_date, comment)
        else:
            st.error("Please enter a valid item name.")

    st.subheader("Remove Inventory")
    if st.button("Remove Inventory"):
        remove_data(barcode_result)

# Load existing Excel data
df = load_data()
st.write("Edit Inventory (Excel)")

# Editable Data Table
edited_df = st.data_editor(df,  num_rows="dynamic")

# Save Changes Button
if st.button("Save Changes to Excel"):
    edited_df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")
    st.success("Changes saved successfully!")
    st.rerun()

# Provide Excel Download Button
excel_data = open(EXCEL_FILE, "rb").read()
st.download_button("Download Excel", excel_data, "inventory.xlsx",
                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
