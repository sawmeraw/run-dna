import json
import pandas as pd

def read_descriptions() -> dict:
    desc = {}
    with open('./model_data.json', 'r') as f:
        desc = json.load(f)

    return desc

def strip_title(title: str) -> str:
    brands = ['Asics', "Brooks", 'Saucony', 'Adidas']

    dashIndex = title.find("-")
    brand_model = title[:dashIndex]

    for brand in brands:
        if brand in brand_model:
            model = brand_model.replace(brand, "")
            print(model.strip())

if __name__ =="__main__":
    SHOPIFY_FILE_PATH = 'description_dir/desc_test_export.csv'
    desc = read_descriptions()

    shopify_df = pd.read_csv(SHOPIFY_FILE_PATH)

    for index, row in shopify_df.iterrows():
        if pd.notna(row['Title']):
            title = row['Title']
            strip_title(title)
