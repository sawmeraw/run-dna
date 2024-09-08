import json
import pandas as pd

def read_descriptions() -> dict:
    desc = {}
    with open('./model_data.json', 'r') as f:
        desc = json.load(f)

    return desc

def strip_title(title: str) -> str:
    brands = ['Asics', "Brooks", 'Saucony', 'Adidas', "On Running", "Hoka", "New Balance", "Nike", "Puma", "Vivobarefoot", "Altra"]

    dashIndex = title.find("-")
    brand_model = title[:dashIndex]

    for brand in brands:
        if brand in brand_model:
            model = brand_model.replace(brand, "")
            return model.strip()
    
    return title

def get_description(raw_desc : str)-> str:

    return raw_desc


if __name__ =="__main__":
    SHOPIFY_FILE_PATH = 'ready to upload/desc_all_processed.csv'
    desc = read_descriptions()

    shopify_df = pd.read_csv(SHOPIFY_FILE_PATH, low_memory=False)

    for index, row in shopify_df.iterrows():
        if pd.notna(row['Title']) and pd.isna(row['Body (HTML)']):  # Process only if Body (HTML) is missing
            title = row['Title']
            model = strip_title(title)
            model_arr = model.lower().split()  # Convert model to lowercase and split

            found = False
            for key in desc.keys():
                key_arr = key.lower().split()  # Convert key to lowercase and split

                # Check if all words in the key are present in the model (case-insensitive)
                if all(word in model_arr for word in key_arr):
                    print(f"Match found for model: {model}, Key: {key}")
                    desc_html = get_description(desc[key])
                    shopify_df.at[index, 'Body (HTML)'] = desc_html  # Update the Body (HTML) column
                    found = True
                    break

            if not found:
                print(f"No match found for model: {model}")
        

    shopify_df.to_csv("./ready to upload/desc_all_processed_3.csv", index=False)

    print('Done')
