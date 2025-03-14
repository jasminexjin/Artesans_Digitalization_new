import pickle
import pandas as pd

PICKLE_FILE = "inventory.pkl"  # Your Pickle file

# Load the pickle file
with open(PICKLE_FILE, "rb") as f:
    data = pickle.load(f)

if isinstance(data, pd.DataFrame) and 'Quantity' in data.columns:
    print(f"Data type of 'Quantity' column: {data['Quantity'].dtype}")

# If it's a Pandas DataFrame, display it
if isinstance(data, pd.DataFrame):
    print(data)  # Print in console

else:
    print("Pickle file does not contain a DataFrame:", data)