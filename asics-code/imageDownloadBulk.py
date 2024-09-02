import pandas as pd
import requests
import os


#CODE WORKS PERFECTLY FOR ASICS, DONT CHANGE ANYTHING



file_name = 'contend9mens_export'

REX_FILE_PATH = os.path.join(os.getcwd(), 'data/rex/asics_rex.csv')
SHOPIFY_FILE_PATH = os.path.join(os.getcwd(), f'data/{file_name}.csv')

rex_df = pd.read_csv(REX_FILE_PATH)
shopify_df = pd.read_csv(SHOPIFY_FILE_PATH)

def strip_title(title):
    if isinstance(title, str):
        startIndex = title.find("(")
        if startIndex != -1:
            return title[:startIndex].strip().replace(' ', '-').lower()
        title = title.replace('-', ' ').strip()
        elements = title.split()
        cleaned_title = '-'.join(elements).lower() 
        return cleaned_title
    return None

def clean_barcode(barcode):
    return barcode.replace("'", "")

def get_product_code(description):
    startIndex = description.find("(")
    endIndex = description.find(")")
    return description[startIndex+1:endIndex]

def sanitize_filename(filename):
    filename = filename.replace("/", "-").replace("\\", "-").replace(" ", "-").replace(":", "-").lower()
    return filename.replace('---', '-').replace('--', '-')

def generate_asics_image_urls(product_code: str):
    item_code = product_code.split('.')[0]
    color_code = product_code.split('.')[1]

    urls = [
        f'https://images.asics.com/is/image/asics/{item_code}_{color_code}_SR_RT_GLB?$zoom$',
        f'https://images.asics.com/is/image/asics/{item_code}_{color_code}_SR_LT_GLB?$zoom$',
        f'https://images.asics.com/is/image/asics/{item_code}_{color_code}_SB_TP_GLB?$zoom$',
        f'https://images.asics.com/is/image/asics/{item_code}_{color_code}_SB_BT_GLB?$zoom$',
        f'https://images.asics.com/is/image/asics/{item_code}_{color_code}_SB_BK_GLB?$zoom$',
        f'https://images.asics.com/is/image/asics/{item_code}_{color_code}_SB_FR_GLB?$zoom$',
    ]

    return urls

products_dict = {}
currTitle = ""

for index, row in shopify_df.iterrows():
    title = row['Title']
    color = row['Option2 Value']
    barcode = clean_barcode(row['Variant SKU'])

    if pd.notna(title):
        currTitle = title

    if pd.notna(color) and pd.notna(barcode):
        stripped_title = sanitize_filename(strip_title(currTitle))
        stripped_color = sanitize_filename(color)
        
        key = f"{stripped_title}-{stripped_color}"
        
        products_dict[key] = barcode

print("Products Dictionary:")
for key, barcode in products_dict.items():
    print(f"Key: {key}, Barcode: {barcode}")

image_save_dir = os.path.join(os.getcwd(), 'images')
os.makedirs(image_save_dir, exist_ok=True)


for key, barcode in products_dict.items():
    found = False
    for _, rex_row in rex_df.iterrows():
        if barcode in rex_row['SupplierSKU']:
            found = True
            description = rex_row['ShortDescription']
            product_code = get_product_code(description)
            print(product_code)
            urls = generate_asics_image_urls(product_code)

            # Download images
            for i, url in enumerate(urls, start=1):
                image_name = sanitize_filename(f"{key}-{i}.jpg")
                image_path = os.path.join(image_save_dir, image_name)

                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        with open(image_path, 'wb') as f:
                            f.write(response.content)
                        print(f"Saved: {image_path}")
                    else:
                        print(f"Failed to download: {url}")
                except Exception as e:
                    print(f"Error downloading {url}: {e}")
            break  # Exit the loop after finding the barcode
    
    if not found:
        print(f"No match found for Barcode: {barcode}")

print("Image download completed.")
