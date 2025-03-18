import re

from rapidfuzz.process import extractOne, extract
from unidecode import unidecode
import pandas as pd
import pickle
from rapidfuzz import process, fuzz
from sentence_transformers import SentenceTransformer, util



def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)  # Remove punctuation and keep only alphanumeric characters and spaces
    text = unidecode(text)  # Convert accented characters to ASCII
    return text

def find_closest_product(product_df, input_name, input_date):
    #normalize the input name and tokenize it

    input_tokens = set(normalize_text(input_name).split())

    expiration_date_norm = normalize_text(input_date)
    product_df["Product Name"] = product_df["Product Name"].astype(str)

    #check if the given product name in the existing product database is a subset of the input token
    def token_match(product_name):
        product_tokens = set(normalize_text(product_name).split())  # Tokenize product name
        return product_tokens.issubset(input_tokens)  # Check if all input tokens exist in product name


    # Apply token-based matching across the DataFrame for Product Name columns
    print(product_df['Product Name'].dtype)
    product_name_results = product_df['Product Name'].apply(token_match)

   # product_date_results = product_df['Expiration Date'].apply(normalize_text) #this exists for me to debug

    #find the matching product in the existing database that matches both name and expiration date
    matched_df = product_df[product_name_results & (product_df['Expiration Date'].apply(normalize_text) == expiration_date_norm)]

    #return a pandas dataframe
    return matched_df if not matched_df.empty else -1
def find_closest_product_fuzzy(product_df, input_name, input_date):
    """
    Find the closest matching product in `product_df` using `rapidfuzz.extractOne`
    based on product name similarity and expiration date.
    """
    # Normalize input values
    input_name_norm = normalize_text(input_name)
    input_date_norm = normalize_text(input_date)

    # Convert 'Product Name' to string and normalize
    product_df["Product Name"] = product_df["Product Name"].astype(str)
    product_name_norm = product_df["Product Name"].apply(normalize_text)

    # Use `rapidfuzz.extractOne` to find the closest match
    #best_match, score, index = extractOne(query=input_name_norm, choices=product_df["Normalized Product Name"], scorer=fuzz.token_sort_ratio)
    choice1, choice2, choice3 = extract(query=input_name_norm, choices=product_name_norm, scorer=fuzz.token_set_ratio, limit=3)
    # Ensure similarity score is above a threshold (e.g., 70 for reasonable match)
    #if score >= 50:
    #matched_row = product_df.iloc[index]  # Get the best-matching row

        # Check if expiration dates also match
    #if normalize_text(matched_row["Expiration Date"]) == input_date_norm:
        #return pd.DataFrame([matched_row])  # Return the matched row as a DataFrame
    #print(score)
    name1,score,index1 = choice1
    name2,score2,index2 = choice2
    name3,score3,index3 = choice3
    selected_index = [index1,index2,index3]

    matched_df = product_df.loc[selected_index]
    return matched_df,selected_index if not matched_df.empty else -1# Return -1 if no valid match is found

def extract_critical_terms(product_name):
    """
    Extract important terms from a product name (e.g., "14G", "16G") to improve matching accuracy.
    """
    pattern = r'\b\d{1,3}(G|mm|ml|GA|in)\b'
    critical_terms = re.findall(pattern, product_name.upper())  # Extract gauge values (14G, 16G)
    return critical_terms  # Returns list of important terms
def match_product_advanced(product_df, input_name, input_date, top_n=3):
    """
    Match input product name with existing products using hybrid fuzzy logic.
    - Uses `WRatio` for improved fuzzy matching.
    - Extracts critical terms (e.g., 14G vs 16G) and prioritizes exact matches.
    - Boosts scores for expiration date matches.
    """
    # Normalize input values
    input_name_norm = normalize_text(input_name)
    input_critical_terms = extract_critical_terms(input_name)

    input_date_norm = normalize_text(input_date) if input_date else None

    # Normalize Product Name column
    product_df["Normalized Product Name"] = product_df["Product Name"].astype(str).apply(normalize_text)

    # Store matching results
    match_results = []

    # Iterate through product names and compute scores
    for idx, row in product_df.iterrows():
        product_name = row["Product Name"]
        product_name_norm = row["Normalized Product Name"]
        expiration_date = row["Expiration Date"]

        # Compute fuzzy match score
        name_score = fuzz.QRatio(input_name_norm, product_name_norm)

        # Extract critical terms from database product
        product_critical_terms = extract_critical_terms(product_name)

        # Prioritize exact matches on critical terms (e.g., 14G vs 16G)
        if input_critical_terms and product_critical_terms:
            if input_critical_terms == product_critical_terms:
                name_score += 15  # Boost score for exact critical term match

        # Boost score for expiration date match
        if input_date_norm and isinstance(expiration_date, str) and normalize_text(expiration_date) == input_date_norm:
            name_score += 10  # Prioritize expiration date matches

        match_results.append((product_name, expiration_date, name_score, idx))

    # Sort results by highest score
    match_results.sort(key=lambda x: x[2], reverse=True)

    # Select top N matches
    best_matches = match_results[:top_n]
    index_list = (product_df.loc[[match[3] for match in best_matches]]).index.tolist()


    # Return DataFrame with top matches
    return product_df.loc[[match[3] for match in best_matches]], index_list

##just me trying things
def find_closest_product_transformer(product_df, input_name, input_date):
    model = SentenceTransformer('all-MiniLM-L6-v2')

    input_name_norm = normalize_text(input_name)
    input_date_norm = normalize_text(input_date)
    product_name_list = (product_df["Product Name"].apply(normalize_text)).tolist()


    embedding_input = model.encode(input_name_norm, convert_to_tensor=True)
    product_embeddings = model.encode(product_name_list, convert_to_tensor=True)

    similarity = util.pytorch_cos_sim(embedding_input, product_embeddings).item()
    best_match_idx = similarity.argmax().item()
    best_match = product_df.iloc[best_match_idx]["Product Name"]

    return best_match



'''
PICKLE_FILE = "inventory_full.pkl"
with open(PICKLE_FILE, "rb") as f:
    data = pickle.load(f)


match = match_product_advanced(data, '50 мл Three part injection disposable sterile syringe ALEXPHARM 50 ml Luer Lock (1-2,40 mm)', '2028-06')

print(match)



###testing


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

