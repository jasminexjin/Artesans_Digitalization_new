import streamlit as st
import io
import re
from google.cloud import vision
from google.cloud import language_v1
from google.cloud import translate_v2 as translate
import tempfile
import os

from sympy.geometry import entity

# Initialize Google Cloud Clients
vision_client = vision.ImageAnnotatorClient()
nlp_client = language_v1.LanguageServiceClient()
translate_client = translate.Client()

# Function to extract text from image using Google Vision
def extract_text_from_image(image):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        temp_file.write(image.read())
        temp_path = temp_file.name

    with io.open(temp_path, "rb") as image_file:
        content = image_file.read()
        image = vision.Image(content=content)

    response = vision_client.text_detection(image=image)
    texts = response.text_annotations

    os.remove(temp_path)

    if texts:
        return texts[0].description  # Extract detected text
    return None

# Function to translate text to English
def translate_to_english(text):
    if not text:
        return "No text detected"
    translation = translate_client.translate(text, target_language="en")
    return translation["translatedText"]

# Function to extract medical product name using Google NLP Entity Recognition
def extract_product_name(text):
    if not text:
        return "No text detected"

    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    response = nlp_client.analyze_entities(document=document)


    for entity in response.entities:
        st.write(entity.type_, entity.name)
        if entity.type_ == language_v1.Entity.Type.CONSUMER_GOOD:  # consumer goods
            return entity.name  # Return detected product name


    return entity.name

# Function to extract expiration date and quantity using regex
def extract_other_details(text):
    if not text:
        return "Not found", "Not found"

    # Extract expiration date using regex
    expiration_date = re.search(r'(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})', text)
    expiration_date = expiration_date.group(0) if expiration_date else "Not found"

    # Extract quantity
    quantity = re.search(r'(\b\d+\s?(pcs|pieces|boxes|packs|units|Qty)\b)', text, re.IGNORECASE)
    quantity = quantity.group(0) if quantity else "Not found"

    return expiration_date, quantity

# Streamlit UI
st.title("Google Cloud Vision + NLP - Medical Supply Scanner")
st.write("Upload an image of a medical product label to detect product name, expiration date, and quantity.")

uploaded_file = st.camera_input('Scan item')

if uploaded_file:
    extracted_text = extract_text_from_image(uploaded_file)
    translated_text = translate_to_english(extracted_text)
    product_name = extract_product_name(translated_text)
    expiration_date, quantity = extract_other_details(translated_text)

    st.subheader("Detected Medical Product Information")
    st.write(f"**Product Name:** {product_name}")
    st.write(f"**Expiration Date:** {expiration_date}")
    st.write(f"**Quantity:** {quantity}")

    with st.expander("See extracted text"):
        st.write(translated_text)
