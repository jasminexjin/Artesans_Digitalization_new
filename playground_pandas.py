import pandas as pd
def test_name(name, df):
    if name in df['Name'].values:
        return True
    else:
        return False

data =  {
    'Name': [ 'test1', 'test2'],
    'Quantity': [1, 6],
    'location': ['no', 'y'],
    'random': [4,None]

}
df = pd.DataFrame(data)
name_to_remove = 'test2'
quantity_to_remove = 6
df.loc[df['Name'] == name_to_remove, "Quantity"] = df.loc[df['Name'] == name_to_remove, "Quantity"] - quantity_to_remove


val =df.loc[df['Name'] == name_to_remove, "Quantity"].values
print(val[0])