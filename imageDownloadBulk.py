import pandas as pd
import requests
import os

file_name = 'misc1_export'

REX_FILE_PATH = os.path.join(os.getcwd(), 'data/rex/brooks_rex.csv')
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

#my knowledge peaked right here
def clean_barcode(barcode):
    return barcode.replace("'", "")

#this hasnt failed, I am surprised
def get_product_code(description):
    startIndex = description.find("(")
    endIndex = description.find(")")
    return description[startIndex+1:endIndex]

#this has gotten out of hand, need to refactor
def sanitize_filename(filename):
    filename = filename.replace("/", "-").replace("\\", "-").replace(" ", "-").replace(":", "-").lower()
    return filename.replace('---', '-').replace('--', '-')

def get_product_code(description : str):
    index = description.find("(")
    productCode = description[index+1:description.find(")")]
    widths = ['A', 'B', 'D', 'E', 'X']
    for width in widths:
        if productCode.find(width) != -1:
            item_code = productCode.split(width)[0]
            color_code = productCode.split(width)[1]
    
    return item_code, color_code

#god almighty method
def generate_brooks_image_urls(item_code, color_code):
    urls = [
        f'https://res.cloudinary.com/dr9fn4qkg/image/upload/w_1367/brooks-images/product-img/{item_code}_{color_code}_l_wr.png',
        f'https://res.cloudinary.com/dr9fn4qkg/image/upload/w_1367/brooks-images/product-img/{item_code}_{color_code}_a_wr.png',
        f'https://res.cloudinary.com/dr9fn4qkg/image/upload/w_1367/brooks-images/product-img/{item_code}_{color_code}_o_wr.png',
        f'https://res.cloudinary.com/dr9fn4qkg/image/upload/w_1367/brooks-images/product-img/{item_code}_{color_code}_m_wr.png',
        f'https://res.cloudinary.com/dr9fn4qkg/image/upload/w_1367/brooks-images/product-img/{item_code}_{color_code}_h_wr.png',
        f'https://res.cloudinary.com/dr9fn4qkg/image/upload/w_1367/brooks-images/product-img/{item_code}_{color_code}_s_wr.png',
    ]
    return urls

products_dict = {}
currTitle = ""

#keep track of the shoes and their colors, avoid downloading same image twice
#and barcode as value to lookup later in rex file to get the product code
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


#loopy ass code but it works
for key, barcode in products_dict.items():
    found = False
    for _, rex_row in rex_df.iterrows():
        barcode = str(barcode)
        supplier_sku = str(rex_row['SupplierSKU'])
        if barcode in supplier_sku:
            found = True
            description = rex_row['ShortDescription']
            item_code, color_code = get_product_code(description)
            
            urls = generate_brooks_image_urls(item_code, color_code)

            # Download images
            for i, url in enumerate(urls, start=1):
                image_name = sanitize_filename(f"{key}-{i}.png")
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
            break
    
    if not found:
        print(f"No match found for Barcode: {barcode}")

print("Image download completed.")
