import os
from google.genai import types
import PIL
import google.genai as genai
import streamlit as st
from google.cloud import vision
import io
import json
import pandas as pd
from dotenv import load_dotenv

load_dotenv()  # Load secrets from .env

# Configure Google Gemini API
api_key = os.getenv('GEMINI_API_KEY')

model =genai.Client(api_key= api_key)
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
            'Product Name': str, 
            'Product Type': str,
            'Expiration Date': str, 
            'Quantity': int
            }
            
            Return "products": list[PRODUCT]

            - "Product Name" should contain the full product name classify the item based on its function (e.g., "IV Catheter", "Syringe", "Gloves", "Bandage"). Ensure the name is accurate and includes all relevant specifications (e.g., gauge, size, type). Include any number that is next to units (i.e 'ml', 'G',or 'mm') but when generate the name, make sure the number has a space between its unit. Make sure the to translate whatever language there is to English. 
            - "Product Type" should classify the item based on its Category in medical term (e.g., A, B, C, D, E, Assorted). 
            - "Expiration Date" should be in the format YYYY-MM-DD or YYYY-MM depending on the product. Locate the hourglass icon on the product packaging. Directly behind or very close to the hourglass, there will be a number printed. This number represents the expiration date. Notice that if the length of the number is 6 digit, most likely it will be in format of YYYYMM. All the expiration year will be at least 2025 or more. Please extract and state the expiration date.
            - "Quantity" should be an integer. If no quantity is detected, return 1.

            Important: Only return a single piece of valid JSON text. Note that sometimes the product name will be in German, French or Ukrainian, please translate all of them to English
            
            **Example Output:**
                ```json
                {
                    "products": [
                    {
                        "product_name": "Vasofix Safety FEP 14 G x 2\" (2,2 x 50 mm) - IV Catheter",
                        "product_type": "A",
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
#image = PIL.Image.open('IMG_1708.png')
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

#any number next to a ml is important plus anz number next to a G is important