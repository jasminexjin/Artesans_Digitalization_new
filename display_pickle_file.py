import pickle
import pandas as pd

PICKLE_FILE = "inventory_full.pkl"  # Your Pickle file

# Load the pickle file
with open(PICKLE_FILE, "rb") as f:
    data = pickle.load(f)

if isinstance(data, pd.DataFrame) and 'Product Name' in data.columns:
    print(f"Data type of 'Product Name' column: {data['Product Name'].dtype}")

# If it's a Pandas DataFrame, display it
if isinstance(data, pd.DataFrame):
    print(data.iloc[263])  # Print in console


else:
    print("Pickle file does not contain a DataFrame:", data)