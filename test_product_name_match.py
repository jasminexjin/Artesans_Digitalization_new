from rapidfuzz import process, fuzz
import re
from unidecode import unidecode
from rapidfuzz.distance import Levenshtein
from rapidfuzz.fuzz import ratio

def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation but keep spaces
    text = unidecode(text)  # Normalize accents (if any)
    return text
#print(normalize_text('BD Neoflon Pro 26 G 0.6 x 19 mm'))

def find_closest_product(input_name, product_names, threshold=90):
    input_name_norm = normalize_text(input_name)

    result= process.extractOne(input_name_norm, product_names,scorer=fuzz.token_sort_ratio)
    return result


product_list = [
    "braun vasofix safety fep 16g x 2 17 x 50 mm iv catheter",
    'bd neoflon pro 26 g 06 x 19 mm',
    '16G BRAUN Catheter'


]
product_name ="16G BRAUN Catheter IV Safety"
 
results = find_closest_product(product_name, product_list)
print(results)

# Test Cases
def test_find_closest_product():
    product_list = [
        "braun vasofix safety fep 16g x 2 17 x 50 mm iv catheter",
        'bd neoflon pro 26 g 06 x 19 mm',
        

    ]
'''
    test_cases = [
        ("Safety V Catheter 16G 2 inch 1.7 x 50mm", "Safety V Catheter 16G x 2\" (1.7 x 50 mm)"),
        # Slight variation in format
       
        ("BRAUN Vasofix Safety FEP 16G x 2\" (1.7 x 50mm) Catheter",
         "BRAUN Vasofix Safety FEP 16G x 2\" (1.7 x 50 mm) IV Catheter"),  # Extra word "Catheter"
        ("B.BRAUN Vasofix Safety FEP 16G x 2\" (1.7 x 50mm)",
         "BRAUN B.BRAUN B Vasofix Safety FEP 16G x 2\" (1.7 x 50 mm)"),  # Variation in brand name
        ("Vasofix Safety FEP 16G x 2\" (1,7 x 50 mm) - 196ml/min",
         "BRAUN Vasofix Safety FEP 16G x 2\" (1,7 x 50 mm) - 196 ml/min"),  # Minor spacing and comma difference
        ("Safety Catheter 14G x 2\"", None),  # Should not match since 14G is different
        ('BD Neoflon™ Pro 26 G 0.6 x 19 mm', 'BD Neoflon Pro 26 G 0.6 x 19 mm')
    ]
    

    for input_name, expected_output in test_cases:
        print('name',input_name)
        result = find_closest_product(input_name, product_list)
        print(result)
        #assert result == expected_output, f"Test failed for input: {input_name}. Expected: {expected_output}, Got: {result}"

    print("All tests passed!")
    
    '''
    
    

#test_find_closest_product()