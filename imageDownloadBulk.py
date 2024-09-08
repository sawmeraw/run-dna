import pandas as pd
import requests
import os

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
def get_product_code(description) -> str:
    startIndex = description.find("(")
    endIndex = description.find(")")
    product_code =  description[startIndex+1:endIndex]
    return product_code

#this has gotten out of hand, need to refactor
def sanitize_filename(filename):
    filename = filename.replace("/", "-").replace("\\", "-").replace(" ", "-").replace(":", "-").lower()
    return filename.replace('---', '-').replace('--', '-')


#god almighty method
def generate_brooks_image_urls(item_code : str):
    urls = [
        f'https://nb.scene7.com/is/image/NB/{item_code}_nb_02_i?$dw_detail_main_lg$&bgc=ffffff&layer=1&bgcolor=ffffff&blendMode=mult&scale=10&wid=1600&hei=1600',
        f'https://nb.scene7.com/is/image/NB/{item_code}_nb_03_i?$dw_detail_main_lg$&bgc=ffffff&layer=1&bgcolor=ffffff&blendMode=mult&scale=10&wid=1600&hei=1600',
        f'https://nb.scene7.com/is/image/NB/{item_code}_nb_04_i?$dw_detail_main_lg$&bgc=ffffff&layer=1&bgcolor=ffffff&blendMode=mult&scale=10&wid=1600&hei=1600',
        f'https://nb.scene7.com/is/image/NB/{item_code}_nb_05_i?$dw_detail_main_lg$&bgc=ffffff&layer=1&bgcolor=ffffff&blendMode=mult&scale=10&wid=1600&hei=1600',
        f'https://nb.scene7.com/is/image/NB/{item_code}_nb_06_i?$dw_detail_main_lg$&bgc=ffffff&layer=1&bgcolor=ffffff&blendMode=mult&scale=10&wid=1600&hei=1600',
        f'https://nb.scene7.com/is/image/NB/{item_code}_nb_07_i?$dw_detail_main_lg$&bgc=ffffff&layer=1&bgcolor=ffffff&blendMode=mult&scale=10&wid=1600&hei=1600',
        
    ]
    return urls


if __name__ == "__main__":
    file_name = 'nbmisc2_export'

    REX_FILE_PATH = os.path.join(os.getcwd(), 'results/rex processed/sent/nb_processed.csv')
    SHOPIFY_FILE_PATH = os.path.join(os.getcwd(), f'data/{file_name}.csv')

    rex_df = pd.read_csv(REX_FILE_PATH)
    shopify_df = pd.read_csv(SHOPIFY_FILE_PATH)

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


    print(f"Products Dictionary: Len({len(products_dict)})")
    for key, barcode in products_dict.items():
        print(f"Key: {key}, Barcode: {barcode}")

    image_save_dir = os.path.join(os.getcwd(), 'images')
    os.makedirs(image_save_dir, exist_ok=True)


    #loopy ass code but it works beautifully
    for key, barcode in products_dict.items():
        found = False
        for _, rex_row in rex_df.iterrows():
            barcode = str(barcode)
            supplier_sku = str(rex_row['SupplierSKU'])
            if barcode in supplier_sku:
                found = True
                description = rex_row['ShortDescription']
                item_code = get_product_code(description)
                stripped_item_code = item_code[: item_code.find("-")]
                
                urls = generate_brooks_image_urls(stripped_item_code.lower())

                # Download images
                for i, url in enumerate(urls, start=1):
                    image_name = sanitize_filename(f"{key}-{i}.png") # THE FILE EXTENSION IS HEREEEEEE
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
