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
import pickle

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
                        "Product Name": "Vasofix Safety FEP 14 G x 2\" (2,2 x 50 mm) - IV Catheter",
                        "Product Type": "A",
                        "Expiration Date": "2026-07-01",
                        "Quantity": 1
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


'''
    :param df: Pandas DataFrame containing product names and expiration dates.
    :param query_name: The product name to search for.
    :param query_expiration: The expiration date to prioritize (can be None).
    :param top_n: Number of best matches to return.
    :return: DataFrame with top N matches, prioritized by expiration date.
'''
def find_closest_product_genai(df, query_name, query_expiration=None, top_n=3 ):
    if "Product Name" not in df.columns:
        raise ValueError("The DataFrame must have a 'Product Name' column.")
    if "Expiration Date" not in df.columns:
        raise ValueError("The DataFrame must have a 'Expiration Date' column.")
    # Convert DataFrame product names to a string for Gemini prompt
    product_list = "\n".join([
        f"Index {index}: {row['Product Name']} (Expiration: {row['Expiration Date'] if pd.notna(row['Expiration Date']) else 'Unknown'})"
        for index, row in df.iterrows()
    ])

    prompt = f"""
        I need to match a product name from a database, with an optional expiration date preference.
        The database contains the following product names with expiration dates:

        {product_list}

        The user is searching for: "{query_name}"
        The expiration date they prefer is: "{query_expiration if query_expiration else 'Any'}"

        Find the **top {top_n} closest matching product names** based on meaning. 
        If possible, prioritize products that also have a matching expiration date.
        Return items that best match in JSON format with **closest matching product names **, its corresponding expiration, its corresponding index, and its corresponding indexes from the original database {df}.

            MATCHES = {{

            'Product Name': str, 
            'Expiration Date': str, 
            'Index': int
            'Quantity': int
            }}

            
            Return 'products': list[MATCHES]
        
        """
    response = model.models.generate_content(
        model=MODEL_ID,
        contents= prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    #converting json to pd
    final_df = convert_json_to_pd(response.text)

    return convert_json_to_pd(response.text)


PICKLE_FILE = "inventory_full.pkl"
with open(PICKLE_FILE, "rb") as f:
    data = pickle.load(f)


match = find_closest_product_genai(data, 'Electrostatic Filter VT 300-1500 ml)', '2025-06-01')

print(match['Index'].dtypes)
'''
'''

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