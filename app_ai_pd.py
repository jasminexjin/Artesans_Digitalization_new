import streamlit as st
import pandas as pd
import cv2
import numpy as np
import os
import google_genai_plugin as genai
import PIL.Image

from inventory_management import *
from find_str import *
import pickle


# Initialize session state for inventory
if "inventory" not in st.session_state:
    st.session_state.inventory = load_inventory()

st.header("Medical Supply Inventory Management")

# Check if an image is uploaded and processed into pd_results
if "pd_results" not in st.session_state:
    st.session_state.pd_results = None  # Placeholder for scanned results

if "matched_results" not in st.session_state:
    st.session_state.matched_results = None  # Placeholder for scanned results

# Image upload section
uploaded_file = st.camera_input("Scan Item")

if uploaded_file:
    #convert uploaded file to the right format
    image = PIL.Image.open(uploaded_file)

    # Process image using Gemini API and convert JSON results to Pandas DataFrame
    json_results = genai.process_medical_supply(image)
    pd_results = genai.convert_json_to_pd(json_results)

    #add the comment section
    pd_results["Comment"] = ''

    # Store scanned results in session state
    st.session_state.pd_results = pd_results

# Initialize inventory only if pd_results exists
if st.session_state.pd_results is not None:
    scanned_products = st.session_state.pd_results

    # Display the scanned product information

    #st.dataframe(st.session_state.pd_results)

    if scanned_products.empty:
        st.warning("No products detected. Please scan again.")
    else:
        st.subheader("Scanned Product Information")

        #editable data that shows scanned product info
        edited_data = st.data_editor(st.session_state.pd_results,num_rows="dynamic", key="edited_data")
        save_inventory(edited_data)
        st.session_state.pd_results = edited_data

        #get info for current product
        name_to_change = st.session_state.pd_results["Product Name"].values
        type_to_change = st.session_state.pd_results["Product Type"].values
        expiration_date_to_change = st.session_state.pd_results["Expiration Date"].values
        comment_to_change = st.session_state.pd_results["Comment"].values


        #get the matching product info
        potential_product = find_closest_product(product_df=st.session_state.inventory, input_name=name_to_change[0],input_date=expiration_date_to_change[0])
        if isinstance(potential_product, pd.DataFrame) and not potential_product.empty:
            st.dataframe(potential_product)
            st.write('Please confirm if this product is correct:')
            if st.button("Confirm My Product"):
                st.session_state.matched_results= potential_product
                st.write('Please select add or remove this product and input the quantity:')
            if st.button("Not My Product"):
                st.session_state.matched_results = st.session_state.pd_results
                st.write('Try Scanning the product again or select Add to add the product as a new item')
        else:
            st.session_state.matched_results = st.session_state.pd_results
            st.write('Product not detected in the inventory, try scanning product again or select Add to add the product as a new item')



        quantity_to_change = st.number_input("Quantity to Add or Remove", min_value=1, step=1)
        # Choose whether to add or remove
        print(st.session_state.inventory["Quantity"].dtype)
        print(type(quantity_to_change))
        left,right = st.columns(2)
        if right.button('Add'):
            name_to_add = st.session_state.matched_results["Product Name"].values
            expiration_date_to_add = st.session_state.matched_results["Expiration Date"].values
            st.session_state.inventory= add_data(st.session_state.inventory,
                                                 name=name_to_add[0],
                                                 type=type_to_change[0],
                                                 expiration_date=expiration_date_to_add[0],
                                                 quantity_to_add=quantity_to_change,
                                                 comment=comment_to_change[0])
            st.success(f'Added {quantity_to_change} of {name_to_change[0]} with expiration date {expiration_date_to_add[0]}.')

        if left.button("Remove"):
            name_to_remove = st.session_state.matched_results["Product Name"].values
            expiration_date_to_remove = st.session_state.matched_results["Expiration Date"].values
            st.session_state.inventory, warning_message = remove_data(st.session_state.inventory,
                                                                      name_to_remove=name_to_remove[0],
                                                                      quantity_to_remove=quantity_to_change,
                                                                      expiration_date=expiration_date_to_remove[0])

            if warning_message:
                st.warning(warning_message)
            else:
                st.success(f'Removed {quantity_to_change} of {name_to_remove[0]} with expiration date {expiration_date_to_remove[0]}.')





st.write("Edit Inventory")



# Editable Data Table
edited_df = st.data_editor(st.session_state.inventory, num_rows="dynamic", key="edited_df")
save_inventory(edited_df)



# Save Changes Button
if st.button("Save Changes to Excel"):
    success_message = save_to_excel(st.session_state.inventory)
    if success_message:
        st.success(success_message)
    else:
        st.error('Data not saved. Please try again')

    st.rerun()

EXCEL_DOWNLOAD_FILE = "test_excel.xlsx"

'''
# Provide Excel Download Button
excel_data = open(EXCEL_DOWNLOAD_FILE, "rb").read()
st.download_button("Download Excel", excel_data, EXCEL_DOWNLOAD_FILE,
                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
'''