import streamlit as st
import pandas as pd
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import os
import google_genai_plugin as genai
import PIL.Image

# Excel file path
EXCEL_FILE = "test_excel.xlsx"


# Function to load existing data or create a new Excel file
def load_data():
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE, engine="openpyxl")
    else:
        df = pd.DataFrame(columns=['Product Name','Product Type', 'Expiration Date', 'Quantity','Comment'])
        df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")
        return df


# Function to save new inventory data to Excel
def save_data(product_name, product_type =None, expiration_date =None, comment =None, quantity = 1):
    df = load_data()
    df["Expiration Date"] = pd.to_datetime(df["Expiration Date"], errors='coerce')

    # Check if the product exists
    if product_name in df["Product Name"].values:
        index = df[df["Product Name"] == product_name].index[0]
        df.loc[index, "Quantity"] += quantity  # Default increment by 1
    else:
        new_entry = pd.DataFrame([[product_name, product_type, expiration_date, quantity, comment]],
                                 columns=['Product Name', 'Product Type', 'Expiration Date', 'Quantity', 'Comment'])
        df = pd.concat([df, new_entry], ignore_index=True)
    current_quantity = df.loc[df["Product Name"]== product_name, "Quantity"]
    df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")
    st.success(f"{quantity}{product_name} added to inventory. Current stock: {current_quantity}")
    st.rerun()


# Function to remove data from Excel
def remove_data(product_name,quantity = 1):
    df = load_data()

    if quantity < 0:
        st.warning("Quantity must be greater than 0!")
        return
    if product_name in df["Product Name"].values:
        # Get the index of the product
        index = df[df['Product Name'] == product_name].index[0]

        # Check if quantity is greater than 0 before decrementing
        if df.loc[index, "Quantity"] >= quantity:
            df.loc[index, "Quantity"] -= quantity
            current_quantity = df.at[index, "Quantity"]
            st.success(f"{quantity} {product_name} removed from the inventory. Current stock: {current_quantity}")
        else:
            st.warning(f"Cannot remove {product_name}, current stock is already less than {quantity} .")
    else:
        st.warning(f"Product {product_name} not found in inventory.")

    # Check if the barcode exists before attempting to remove it
    #df.loc[df["Product Name"] == product_name, "Quantity"] -= quantity

    df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")
    st.warning("Inventory item removed successfully!")
    st.rerun()


#this is where front end starts
# Initialize session state for inventory
if "inventory" not in st.session_state:
    st.session_state.inventory = load_data()

st.title("Medical Supply Inventory Management")

# Display existing inventory from Excel
#st.subheader("Current Inventory")
#st.dataframe(st.session_state.inventory)

# Check if an image is uploaded and processed into pd_results
if "pd_results" not in st.session_state:
    st.session_state.pd_results = None  # Placeholder for scanned results

# Image upload section
uploaded_file = st.camera_input("Scan Item")

if uploaded_file:
    #convert uploaded file to the right format
    image = PIL.Image.open(uploaded_file)

    # Process image using Gemini API and convert JSON results to Pandas DataFrame
    json_results = genai.process_medical_supply(image)
    pd_results = genai.convert_json_to_pd(json_results)

    with st.status('Processing...'):
        st.write('Processing Image...')


    # Store scanned results in session state
    st.session_state.pd_results = pd_results

# Initialize inventory only if pd_results exists
if st.session_state.pd_results is not None:
    scanned_products = st.session_state.pd_results.copy()
    scanned_products.rename(columns={
        "product_name": "Product Name",
        "product_type": "Product Type",
        "expiration_date": "Expiration Date",
        "quantity": "Quantity"
    }, inplace=True)

    # Display the scanned product information
    #st.subheader("Scanned Product Information")
    #st.dataframe(scanned_products)

    # User selects an item from the detected products
    st.write("Scanned Data:", scanned_products)
    st.write("Columns:", scanned_products.columns.tolist())
    product_names = scanned_products["Product Name"].tolist()




    if not product_names:
        st.warning("No products detected. Please scan again.")
    else:
        selected_product = st.selectbox("Select a product", product_names)

        # Choose whether to add or remove
        action = st.radio("Action", ["Add", "Remove"])

        # Get the current quantity of the selected product from inventory
        current_quantity = st.session_state.inventory.loc[
            st.session_state.inventory["Product Name"] == selected_product, "Quantity"
        ].values[0] if selected_product in st.session_state.inventory["Product Name"].values else 0

        if action == "Remove":
            max_quantity = min(current_quantity, 100)  # Prevent excessive removal
            quantity_to_remove = st.number_input("Quantity to Remove", min_value=1, value=1,max_value=max_quantity, step=1)
            st.write(quantity_to_remove)

            if st.button("Remove from Inventory"):
                remove_data(selected_product, quantity_to_remove)

        elif action == "Add":
            quantity_to_add = st.number_input("Quantity to Add", min_value=1, value=1, step=1)

            if st.button("Add to Inventory"):

                matching_products = scanned_products[scanned_products["Product Name"] == selected_product]
                if not matching_products.empty:
                    product_info = matching_products.iloc[0]
                    save_data(
                        product_name=selected_product,
                        product_type=product_info.get("Product Type", None),
                        expiration_date=product_info.get("Expiration Date", None),
                        comment=""
                    )
                else:
                    st.error("Selected product not found in scanned data!")

    # Display updated inventory
    st.subheader("Updated Inventory")
    st.dataframe(load_data())  # Reload from Excel after updates
else:
    st.info("Please scan an item to proceed.")

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
