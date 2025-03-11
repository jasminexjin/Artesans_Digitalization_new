import streamlit as st
import io
import re
from google.cloud import vision
import tempfile
import os

# Initialize Google Cloud Vision Client
client = vision.ImageAnnotatorClient()


credential_path = "dark-valor-453012-q2-a28fb47690d0.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

# Function to process image and extract text
def extract_text_from_image(image):
    # Save image to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        temp_file.write(image.read())
        temp_path = temp_file.name

    # Read image content
    with io.open(temp_path, "rb") as image_file:
        content = image_file.read()
        image = vision.Image(content=content)

    # Perform OCR with Google Vision
    response = client.text_detection(image=image)
    texts = response.text_annotations

    # Delete the temporary file
    os.remove(temp_path)

    if texts:
        return texts[0].description  # Extract detected text
    else:
        return None

# Function to extract product details from text
def extract_product_details(text):
    if not text:
        return "No text detected", "Not found", "Not found"

    # Extract product name (First few words, assuming they contain product name)
    product_name = text.split("\n")[0]  

    # Extract expiration date using regex (common formats: MM/DD/YYYY, YYYY-MM-DD)
    expiration_date = re.search(r'(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})', text)
    expiration_date = expiration_date.group(0) if expiration_date else "Not found"

    # Extract quantity (search for patterns like "Qty: 10" or "10 pieces")
    quantity = re.search(r'(\b\d+\s?(pcs|pieces|boxes|packs|units|Qty)\b)', text, re.IGNORECASE)
    quantity = quantity.group(0) if quantity else "Not found"

    return product_name, expiration_date, quantity

# Streamlit UI
st.title("Google Cloud Vision - Product Scanner")
st.write("Upload an image of a product label to detect product name, expiration date, and quantity.")

# Upload image
uploaded_file = st.camera_input("Scan Barcode or QR Code")

if uploaded_file:
    # Extract text from image
    extracted_text = extract_text_from_image(uploaded_file)

    # Extract product details
    product_name, expiration_date, quantity = extract_product_details(extracted_text)

    # Display results
    st.subheader("Detected Product Information")
    st.write(f"**Product Name:** {product_name}")
    st.write(f"**Expiration Date:** {expiration_date}")
    st.write(f"**Quantity:** {quantity}")

    # Display extracted raw text for debugging
    with st.expander("See extracted text"):
        st.write(extracted_text)
