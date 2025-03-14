import pandas as pd
import pickle

from inventory_management import PICKLE_FILE

EXCEL_PATH = "/Users/illiabilokonov/Downloads/existing_data.xlsx"
PICKLE_FILE = 'inventory.pkl'

df = pd.read_excel(EXCEL_PATH)

print(df.columns)

if 'Expiration Date' in df.columns:
    pd.to_datetime(df['Expiration Date'], format='%Y%m%d', errors='coerce')
    df['Expiration Date'] = df['Expiration Date'].astype(str)
    print('success')



if 'Expiration Date' in df.columns:
    df['Expiration Date'] = df['Expiration Date'].str.split(" ").str[0]
    print('success')

if 'Quantity' in df.columns:
    pd.to_numeric(df['Quantity'], errors='coerce')
    df['Quantity'] = df['Quantity'].fillna(0)
    print(type(df['Quantity'][0]))
    #df['Quantity'] = df['Quantity'].astype('Int64')
    print('success')

'''
for i in range(len(df)):
    if 'Expiration Date' in df.columns:
        print(df.loc[i, "Expiration Date"])

'''

#pd.to_datetime(df.loc[:,'Expiration Date'], format='%Y%m%d', errors='coerce')

#df= df.loc[:,"Expiration Date"].str.split(" ").str[0]
print(type(df['Quantity'][0]))
print(type(df['Expiration Date'][1]))
print(type(df['Product Name'][1]))
print(type(df['Comment'][1]))


print(type(df))


def df_to_pickle(df, PICKLE_FILE):
    if not isinstance(df, pd.DataFrame):  # Ensure it's a DataFrame
        raise ValueError("Input must be a DataFrame")

    with open(PICKLE_FILE, "wb") as f:
        pickle.dump(df, f)

df_to_pickle(df, PICKLE_FILE)





#upload to pickle
#with open(PICKLE_FILE, "wb") as f:
    #pickle.dump(df, f)

