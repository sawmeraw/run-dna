import pandas as pd
import json

def strip_title(title):
    if isinstance(title, str):
        elements= title.split(' ')
        cleaned_elements = []
        for i,elem  in enumerate(elements):
            if elem == '-':
                continue
            if '(' in elem or ')' in elem:
                continue
            
            cleaned_elements.append(elem)
        return ' '.join(cleaned_elements).strip().replace(' ', '-').lower()
    
def strip_color(color):
    if isinstance(color, str):
        return color.replace('/', '-').replace(' ', '-').lower()

def get_image_name(title:str, color: str)-> dict:
    stripped_title =strip_title(title)
    stripped_color =strip_color(color)
    return f'{stripped_title}-{stripped_color}-1'


def first_pass(df: pd.DataFrame)-> dict:
    data = {}
    currTitle = ""
    for index, row in df.iterrows():
        if pd.notna(row['Title']):
            currTitle = row['Title']
        
        color= row['Option2 Value']

        image_name = get_image_name(currTitle, color=color)

        key = (currTitle, color)
        if key not in data:
            data[key] = image_name
            print(f"Added {key} with image: {image_name}")
        
    return data


def second_pass(df: pd.DataFrame, data: dict):

    currTitle = ""    
    for index, row in df.iterrows():
        if pd.notna(row['Title']):
            currTitle = row['Title']

        currentColor = row['Option2 Value']
        img_src = str(row['Image Src']).strip()   
        if not img_src or img_src == 'nan':
            continue

        for key, image_name in data.items():
            if image_name in img_src:
                data[key] = img_src
                print(f"Updated {key} with full Img Src: {img_src}")
                break
             
    return data

def third_pass(df: pd.DataFrame, data: dict):
    """
    Third pass: Update the 'Variant Image' column in the dataframe based on the dictionary.
    """
    currTitle = ""
    
    for index, row in df.iterrows():
        if pd.notna(row['Title']):
            currTitle = row['Title']

        currentColor = row['Option2 Value']
        key = (currTitle, currentColor)

        if key in data:
            df.at[index, 'Variant Image'] = data[key]

    return df

if __name__ == "__main__":
    SHOPIFY_FILE = './products_export.csv'

    df = pd.read_csv(SHOPIFY_FILE, low_memory=False)

    data = first_pass(df)

    data_new = second_pass(df, data)

    new_df = third_pass(df, data)

    output_file = './updated_variants.csv'
    df.to_csv(output_file, index=False)

    print(f"Variant images updated and saved to {output_file}")

