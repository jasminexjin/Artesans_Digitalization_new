import streamlit as st
import pandas as pd
import os
import pickle


PICKLE_FILE = "inventory.pkl"

data =  {
    'Name': [ 'test1', 'test2'],
    'Quantity': [1, 2]
}

#load inventory from a pickle
def load_inventory():
    """Loads inventory from a pickle file into session state or initializes default inventory."""
    if os.path.exists(PICKLE_FILE):
        with open(PICKLE_FILE, "rb") as f:
            return pickle.load(f)
    else:
        inventory_df = pd.DataFrame(columns=['Product Name', 'Product Type', 'Expiration Date', 'Quantity', 'Comment'])
        save_inventory(inventory_df)
        return inventory_df

# save inventory dataframe to a pickle file
def save_inventory(inventory_df):
    with open(PICKLE_FILE, "wb") as f:
        pickle.dump(inventory_df, f)


def add_data( inventory_df, name_to_add, quantity_to_add):
    df = st.session_state.inventory_df  # Access session state DataFrame
    if name_to_add in df["Name"].values:
        df.loc[df["Name"] == name_to_add, "Quantity"] += quantity_to_add
    else:
        new_entry = pd.DataFrame([{'Name': name_to_add, 'Quantity': quantity_to_add}])
        st.session_state.inventory_df = pd.concat([df, new_entry], ignore_index=True)

    save_inventory()  # Save changes to Pickle


def remove_data(name_to_remove, quantity_to_remove):
    df = st.session_state.inventory_df  # Access session state DataFrame
    if name_to_remove in df["Name"].values:
        quantity_values = df.loc[df["Name"] == name_to_remove, 'Quantity'].values
        if quantity_values[0] >= quantity_to_remove:
            df.loc[df["Name"] == name_to_remove, "Quantity"] -= quantity_to_remove
            save_inventory()  # Save changes to Pickle
        else:
            st.warning(f'Insufficient stock: Only {quantity_values[0]} available.')
    else:
        st.warning(f'{name_to_remove} not found in inventory.')

st.header("Inventory Management")

name = st.text_input('Enter Product Name:')
quantity = st.number_input('Enter Quantity:', min_value=1, step=1)

if st.button('Add'):
    add_data(name, quantity)


name_to_remove = st.text_input("Name to Remove:")
quantity_to_remove = st.number_input("Quantity to Remove:", min_value=1, step=1)

if st.button('Remove'):
    remove_data(name_to_remove, quantity_to_remove)

# Display Updated Inventory
st.dataframe(st.session_state.inventory_df)




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