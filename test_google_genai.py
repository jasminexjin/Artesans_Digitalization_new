import os
from google.genai import types
import PIL
import google.genai as genai
import streamlit as st
from google.cloud import vision
import io
import json
import pandas as pd


# Configure Google Gemini API
my_key = 'AIzaSyBwOV57JRpjO1VVBcJHGBpliSR03K-4WD4'
model =genai.Client(api_key= my_key)
MODEL_ID = "gemini-1.5-pro"


#Translating Image to text with GenAI - I think it is better accuracy to do the transcribing and words detection together
'''
def image_to_text(image):
    response = model.models.generate_content(
        model = MODEL_ID,
        contents = ['transcribe all the text in this image and translate them into English if it is not already',image]
    )
    return response.text

'''


# converting json to pandas dataframe
def convert_json_to_pd(json_data):
    data_dict = json.loads(json_data)
    df = pd.DataFrame(data_dict['products'])
    return df


# Function to process medical supply labels using Gemini 1.5 Vision
def process_medical_supply(image):

    prompt = """
            Please return JSON describing the product name with product specification, expiration date, and quantity of the products using the following schema:

            {
            "products": list[PRODUCT]
            }

            PRODUCT = {
            'product_name': str, 
            'product_type': str,
            'expiration_date': str, 
            'quantity': int
            }
            
            Return "products": list[PRODUCT]

            - "product_name" should contain the **full name of the product**, including any key specifications from the label.
            - "product_type" should classify the item based on its function (e.g., "IV Catheter", "Syringe", "Gloves", "Bandage"). If uncertain, infer the most likely category based on the text.
            - "expiration_date" should be in the format YYYY-MM-DD. If no expiration date is detected, return "Unknown".
            - "quantity" should be an integer. If no quantity is detected, return 1.

            Important: Only return a single piece of valid JSON text.
            
            **Example Output:**
                ```json
                {
                    "products": [
                    {
                        "product_name": "Vasofix Safety FEP 14 G x 2\" (2,2 x 50 mm) - IV Catheter",
                        "product_type": "IV Catheter",
                        "expiration_date": "2026-07-01",
                        "quantity": 1
                    }
                    ]

            Here is the provided text:
            """ #+ image_to_text(image)



    response = model.models.generate_content(
        model= MODEL_ID,
        contents=[prompt, image],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    # Returns structured product details
    try:
        return response.text  # Convert response to dictionary
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON response from Gemini API"}



#Testing genai
#image = PIL.Image.open("IMG_1708.png")
#print(process_medical_supply(image))
#print(json.dumps(json.loads(process_medical_supply(image))))

'''
# Streamlit UI
st.title("Medical Supply Scanner with Google Gemini Vision")
st.write("Upload an image of a medical product label to detect product details.")

uploaded_file = st.camera_input("Scan item")

if uploaded_file:
    image = PIL.Image.open(uploaded_file)

    # Process image with Gemini Vision
    st.write("Processing...")
    product_info = process_medical_supply(image)

    st.subheader("Detected Product Information")
    st.json(json.loads(product_info))  # Display structured JSON output
'''