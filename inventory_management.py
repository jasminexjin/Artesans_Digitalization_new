import streamlit as st
import pandas as pd
import os
import pickle

from narwhals import DataFrame

import find_str as fs


PICKLE_FILE = "inventory_full.pkl"
EXCEL_FILE = "inventory.xlsx"


#load inventory from a pickle
def load_inventory():
    """Loads inventory from a pickle file into session state or initializes default inventory."""
    if os.path.exists(PICKLE_FILE):
        with open(PICKLE_FILE, "rb") as f:
            return pickle.load(f)
    else:
        df = pd.DataFrame(columns=['Product Name', 'Product Type', 'Expiration Date', 'Quantity', 'Comment'])
        save_inventory(df)
        return df

# save inventory dataframe to a pickle file
def save_inventory(df):
    with open(PICKLE_FILE, "wb") as f:
        pickle.dump(df, f)
def display_selected_product(df,input_name,expiration_date ):
    return

def match_products(df, input_name,expiration_date):
    matched_df = fs.find_closest_product(product_df=df, input_name=input_name, input_date=expiration_date)
    if isinstance(matched_df, pd.DataFrame) and not matched_df.empty:
        # Iterate through all matches in new_df (if there are multiple)
        for _, match_row in matched_df.iterrows():
            matched_index = df.loc[
                (df['Product Name'] == match_row['Product Name']) &
                (df['Expiration Date'] == match_row['Expiration Date'])
                ].index.tolist()
    else:
        matched_df, matched_index= fs.match_product_advanced(product_df=df, input_name=input_name, input_date=expiration_date, top_n=3)

    return matched_index


def add_data(df, name, matched_index, type = None , expiration_date = None, quantity_to_add = 1, comment =None):
    st.write(f'inside add {matched_index}')
    if isinstance(matched_index, int) and matched_index >= 0:
        st.write('its inside')
        df.loc[matched_index, "Quantity"] += quantity_to_add
        #only the quantity that matches the product name and expiration date is add, first in the list
    else:
        new_entry = pd.DataFrame([{'Product Name': name,
                                   'Product Type': type,
                                   'Expiration Date': expiration_date,
                                   'Quantity': quantity_to_add,
                                   'Comment': comment}])
        df = pd.concat([df, new_entry], ignore_index=True)

    save_inventory(df)# Save changes to Pickle
    return df


def remove_data(df, matched_index,name_to_remove, type = None , expiration_date = None, quantity_to_remove = 1, comment =None):
    if isinstance(matched_index, int) and matched_index > 0:
        #get the current quantity that matches with the matched index
        quantity_values = df.loc[matched_index, "Quantity"]
        if quantity_values >= quantity_to_remove:
            #only the quantity associated with the name is removed
            #df.loc[df['Product Name'] == name_to_remove, "Quantity"] -= quantity_to_remove this one does not work for some reason
            df.loc[matched_index, "Quantity"] = df.loc[matched_index, "Quantity"] - quantity_to_remove
            save_inventory(df)  # Save changes to Pickle
            return df, None
        else:
            return df, f'Insufficient stock: Only {quantity_values} available for {name_to_remove} with expiration date {expiration_date}.'
    else:
        return df, f'{name_to_remove} with expiration date {expiration_date} not found in inventory.'
    return df, None

def save_to_excel(df):
    df.to_excel(EXCEL_FILE, index=False, engine="openpyxl")
    return 'Saved to Excel'


'''
st.header("Inventory Management")

name = st.text_input('Enter Product Name:')
quantity = st.number_input('Enter Quantity:', min_value=1, step=1)

if st.button('Add'):
    st.session_state.inventory_df = add_data(st.session_state.inventory_df, name, quantity_to_add=quantity)


name_to_remove = st.text_input("Name to Remove:")
quantity_to_remove = st.number_input("Quantity to Remove:", min_value=1, step=1)

if st.button('Remove'):
    remove_data(name_to_remove, quantity_to_remove)

# Display Updated Inventory
st.dataframe(st.session_state.inventory_df)

'''


'''

# test add and remove data
add_data('test3',3)
print(inventory_df)

load_data()
print(inventory_df)

remove_data('test3',2)
print(inventory_df)

remove_data('test2',1)
print(inventory_df)

remove_data('test1',1)
print(inventory_df)

add_data('test1',10)
print(inventory_df)

add_data('test4',11)
print(inventory_df)

load_data()
print(inventory_df)

'''