import streamlit as st
import pandas as pd
from inventory_management import *
from google_genai_plugin import *

# Sample DataFrame (Replace this with your actual filtered DataFrame)
data = {
    "Product Name": ["IV Catheter 14G", "Suctin Catheter Ch16", "Manual Suction Pumps"],
    "Expiration Date": ["2025-12-31", "2026-06-15", "2027-01-01"],
    "Quantity": [10, 15, 20]  # Example additional column
}

df = pd.DataFrame(data)

if 'product_inv' not in st.session_state:
    st.session_state.product_inv = load_inventory()

# Store the filtered DataFrame in session state (if not already stored)
if "filtered_products" not in st.session_state:
    st.session_state.filtered_products = df

if "choice" not in st.session_state:
    st.session_state.choice = None

#iterate through the data list to get each product and generate a list of matching product, return their index

'''
for _, match_row in df.iterrows():
    name = match_row['Product Name']
    st.write(match_row['Product Name'])
    expiration_date = match_row['Expiration Date']
    index_list = match_products(df = st.session_state.product_inv, input_name=name, expiration_date=expiration_date)
'''

first_row = df.iloc[2]
# Extract values
name = first_row['Product Name']
expiration_date = first_row['Expiration Date']
# Display in Streamlit
st.write(f"Testing first product: {name}, Expiration Date: {expiration_date}")
# Run the function on the first product
index_list = match_products(df=st.session_state.product_inv, input_name=name, expiration_date=expiration_date)


choice = pd.DataFrame(columns=['Product Name', 'Expiration Date','Quantity','Index'])
product = st.session_state.product_inv
for i in range(len(index_list)):
    new = pd.DataFrame([{
        'Product Name' : product.loc[index_list[i], "Product Name"],
        'Expiration Date' : product.loc[index_list[i], 'Expiration Date'],
        'Quantity': product.loc[index_list[i], 'Quantity'],
        'Index' : index_list[i]
    }])
    choice = pd.concat([choice, new])
st.session_state.choice = choice

st.write("### Select a Product")

# Generate selection options with a unique identifier
choice["Selection Label"] = choice.apply(lambda row: f"{row['Product Name']} (Exp: {row['Expiration Date']}) (#: {row['Quantity']}) (Index: {row['Index']})", axis=1)

# Let the user select a row
selected_label = st.radio("Choose a product:", choice["Selection Label"])

# Find the selected row in the DataFrame
selected_row = choice[choice["Selection Label"] == selected_label]

if st.button("confirm selection"):
    st.session_state.selected_product = selected_row.iloc[0]
else:
    st.write("### No selection made")

# Store selected row in session state for future reference


quantity = st.session_state.filtered_products ["Quantity"]
st.dataframe(st.session_state.selected_product)
st.write(f"### Selected Product Details{quantity}")


