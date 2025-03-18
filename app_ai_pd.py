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
    st.session_state.inventory['Product Name'] = st.session_state.inventory['Product Name'].astype(str)
    st.session_state.inventory['Quantity'] = pd.to_numeric(st.session_state.inventory['Quantity'])

st.header("Medical Supply Inventory Management")

# Check if an image is uploaded and processed into pd_results
if "pd_results" not in st.session_state:
    st.session_state.pd_results = None  # Placeholder for scanned results

if "matched_results" not in st.session_state:
    st.session_state.matched_results = pd.DataFrame()  # Placeholder for matched results

if "choice" not in st.session_state:
    st.session_state.choice = None

if "selected_label" not in st.session_state:
    st.session_state.selected_label = None

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
        data_for_edit = st.session_state.pd_results.copy()
        edited_data = st.data_editor(data_for_edit,num_rows="dynamic", key="edited_data")
        #if not edited_data.equals(st.session_state.pd_results):
            #st.session_state.pd_results = edited_data

        #get info for current product
        name_to_change = edited_data["Product Name"].values
        type_to_change = st.session_state.pd_results["Product Type"].values
        expiration_date_to_change = st.session_state.pd_results["Expiration Date"].values
        comment_to_change = st.session_state.pd_results["Comment"].values

        #get the matching product index (index in the inventory)
        index_list = match_products(df=st.session_state.inventory, input_name=name_to_change[0], expiration_date=expiration_date_to_change[0])
        st.write(index_list)
        choice = pd.DataFrame(columns=['Product Name', 'Expiration Date','Quantity' ,'Index'])
        product = st.session_state.inventory

       #add the Product Name and expiration date in choice
        for i in range(len(index_list)):
            new = pd.DataFrame([{
                'Product Name': product.loc[index_list[i], "Product Name"],
                'Expiration Date': product.loc[index_list[i], 'Expiration Date'],
                'Quantity': product.loc[index_list[i], 'Quantity'],
                'Index': index_list[i]
            }])
            choice = pd.concat([choice, new])

        #added back to corresponding session states
        st.session_state.choice = choice
        st.dataframe(choice)
        st.session_state.choice = st.session_state.choice.sort_values(
            by=["Product Name", "Expiration Date"]).reset_index(drop=True)

        st.write("### Select a Product")
        # Generate selection options with a unique identifier
        st.session_state.choice["Selection Label"] = st.session_state.choice.apply(
            lambda row: f"{row['Product Name']} (Exp: {row['Expiration Date']})  (#: {row['Quantity']}) (Index: {row['Index']})", axis=1)

        # Maintain previous selection if exists
        selection_options = st.session_state.choice["Selection Label"].tolist()
        prev_selection = selection_options.index(
            st.session_state.selected_label) if st.session_state.selected_label in selection_options else 0

        # Let the user select a row
        selected_label = st.radio("Choose a product:", selection_options)
        st.session_state.selected_label = selected_label

        # Find the selected row in the DataFrame
        potential_product = st.session_state.choice[st.session_state.choice["Selection Label"] == selected_label]

        if isinstance(potential_product, pd.DataFrame) and not potential_product.empty:
            col1,col2 = st.columns(2)
            st.write('Please confirm if this product is correct:')
            with col1:
                if st.button("Confirm My Product"):
                    st.session_state.matched_results= potential_product
                    st.write('Please select add or remove this product and input the quantity:')
                    st.dataframe(st.session_state.matched_results)
            with col2:
                if st.button("None of the Above"):
                    st.session_state.matched_results = st.session_state.pd_results
                    st.write('Try Scanning the product again or select Add to add the product as a new item')
                    st.dataframe(st.session_state.matched_results)
        else:

            st.write('Product not detected in the inventory, try scanning product again or select Add to add the product as a new item')


        if st.session_state.matched_results.empty:
            st.warning('Please Confirm if this product is correct before proceeding to add or remove')

        quantity_to_change = st.number_input("Quantity to Add or Remove", min_value=1, step=1)

        left,right = st.columns(2)
        if right.button('Add'):
            name_to_add = st.session_state.matched_results["Product Name"].values
            expiration_date_to_add = st.session_state.matched_results["Expiration Date"].values
            if 'Index' in st.session_state.matched_results:
                matched_index = st.session_state.matched_results["Index"].values

            else:
                matched_index = 0
            st.write(matched_index)

            st.session_state.inventory= add_data(st.session_state.inventory,
                                                 name=name_to_add[0],
                                                 matched_index=matched_index[0],
                                                 type=type_to_change[0],
                                                 expiration_date=expiration_date_to_add[0],
                                                 quantity_to_add=quantity_to_change,
                                                 comment=comment_to_change[0])
            st.success(f'Added {quantity_to_change} of {name_to_add[0]} with expiration date {expiration_date_to_add[0]}.')

        if left.button("Remove"):
            name_to_remove = st.session_state.matched_results["Product Name"].values
            expiration_date_to_remove = st.session_state.matched_results["Expiration Date"].values
            matched_index = st.session_state.matched_results["Index"].values
            #st.write(type(matched_index[0]))
            st.session_state.inventory, warning_message = remove_data(st.session_state.inventory,
                                                                      name_to_remove=name_to_remove[0],
                                                                      matched_index=matched_index[0],
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