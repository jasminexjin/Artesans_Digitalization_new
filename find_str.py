import re
from unidecode import unidecode
import pandas as pd
import pickle



def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)  # Remove punctuation and keep only alphanumeric characters and spaces
    text = unidecode(text)  # Convert accented characters to ASCII
    return text

def find_closest_product(product_df, input_name, input_date):
    #normalize the input name and tokenize it

    input_tokens = set(normalize_text(input_name).split())

    expiration_date_norm = normalize_text(input_date)

    #check if the given product name in the existing product database is a subset of the input token
    def token_match(product_name):
        product_tokens = set(normalize_text(product_name).split())  # Tokenize product name
        return product_tokens.issubset(input_tokens)  # Check if all input tokens exist in product name


    # Apply token-based matching across the DataFrame for Product Name columns
    product_name_results = product_df['Product Name'].apply(token_match)
    product_date_results = product_df['Expiration Date'].apply(normalize_text) #this exists for me to debug

    #find the matching product in the existing database that matches both name and expiration date
    matched_df = product_df[product_name_results & (product_df['Expiration Date'].apply(normalize_text) == expiration_date_norm)]

    #return a pandas dataframe
    return matched_df if not matched_df.empty else -1

PICKLE_FILE = "inventory.pkl"
with open(PICKLE_FILE, "rb") as f:
    data = pickle.load(f)


match = find_closest_product(data, '50 мл Three-part injection disposable sterile syringe ALEXPHARM 50 ml Luer Lock (1-2,40 mm)', '2028-06')

print(isinstance(match, pd.DataFrame))


###testing
'''

test = {
    'Product Name': ['Original Perfusor Syringe 50 ml Luer Lock',
                     'Vasofix Safety FEP 22G 220x1 (0,9 x 25 mm)',
                     '50 ml Luer Lock Syringe with needle, 18G (1.2 x 40 mm)',
                     '24G PUR 240 (0,7 x 19 mm) IV Catheter'],

    "Expiration Date": [
        "2025-12-31",
        "2024-06-15",
        "2026-08-20",
        "2025-05-10"
    ]
}
product_list = {'Product Name':['syringe 50 ml',
                                'syringe 50 ml',
                                'IV Catheter',
                                ],
                "Expiration Date": ["2025-12-30",
                                    "2026-08-20",
                                    "2024-06-15",
                                    ]
                    }
product_df = pd.DataFrame(product_list)
df1 = pd.DataFrame(test)
inputs = pd.DataFrame(
    {'Product Name': ['syringe 50 ml', 'IV Catheter']})

for index, row in df1.iterrows():
    product_name = row['Product Name']
    expiration_date = row['Expiration Date']
    new_df = find_closest_product(input_name=product_name, product_df = product_df, input_date=expiration_date)
    if isinstance(new_df, pd.DataFrame) and not new_df.empty:
        # Iterate through all matches in new_df (if there are multiple)
        for _, match_row in new_df.iterrows():
            matched_index = product_df.loc[
                (product_df['Product Name'] == match_row['Product Name']) &
                (product_df['Expiration Date'] == match_row['Expiration Date'])
                ].index.tolist()
            print(matched_index)

    
    if isinstance(new_df, pd.DataFrame):
        matched_index = product_df.loc[(product_df['Product Name'].values[0] == new_df['Product Name'].values[0]) &
                               (product_df['Expiration Date'].values[0] == new_df['Expiration Date'].values[0])].index.tolist()

       
        print(new_df['Expiration Date'].values[0])


print(normalize_text('2026-09-01'))

df2 = pd.DataFrame({'Product Name':['syringe 50 ml', 'IV Catheter']})

for i in inputs['Product Name']:
    print(find_closest_product_name(i,df2))



product_name ='syringe 50 ml'

test = {
        'Product Name' : ['Original Perfusor Syringe 50 ml Luer Lock',
        'Vasofix Safety FEP 22G 220x1 (0,9 x 25 mm)',
        '50 ml Luer Lock Syringe with needle, 18G (1.2 x 40 mm)',
        '24G PUR 240 (0,7 x 19 mm) IV Catheter']
        
        "Expiration Date": [
        "2025-12-31",
        "2024-06-15",
        "2026-08-20",
        "2025-05-10"
    ]
}
        



for name in test:
    print(name)
    name_new = set(normalize_text(name).split())
    print(name_new)
    product_set = set(product_name.split())
    print(product_set)
    if product_set.issubset(name_new):
        print('Found')
    else:
        print('Not found')
    # trying out find method
    #print(name_new.find(product_name))
    

'''

