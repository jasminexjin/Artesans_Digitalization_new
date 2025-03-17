import streamlit as st
import pandas as pd

# Sample DataFrame (Replace this with your actual filtered DataFrame)
data = {
    "Product Name": ["Ibuprofen", "Vitamin C", "Painkiller"],
    "Expiration Date": ["2025-12-31", "2026-06-15", "2027-01-01"],
    "Quantity": [10, 15, 20]  # Example additional column
}
df = pd.DataFrame(data)

# Store the filtered DataFrame in session state (if not already stored)
if "filtered_products" not in st.session_state:
    st.session_state.filtered_products = df

st.write("### Select a Product")

# Generate selection options with a unique identifier
df["Selection Label"] = df.apply(lambda row: f"{row['Product Name']} (Exp: {row['Expiration Date']})", axis=1)

# Let the user select a row
selected_label = st.radio("Choose a product:", df["Selection Label"])

# Find the selected row in the DataFrame
selected_row = df[df["Selection Label"] == selected_label]

if st.button("confirm selection"):
    st.session_state.selected_product = selected_row.iloc[0]
else:
    st.write("### No selection made")

# Store selected row in session state for future reference
if not selected_row.empty:
    st.session_state.selected_product = selected_row.iloc[0]  # Store as Series

quantity = st.session_state.filtered_products ["Quantity"]
st.dataframe(selected_row)
st.write(f"### Selected Product Details{quantity}")
st.write(st.session_state.selected_product)

