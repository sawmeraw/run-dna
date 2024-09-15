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
def generate_asics_image_urls(item_code : str, color_code: str):
    urls = [
        f'https://images.asics.com/is/image/asics/{item_code}_{color_code}_SR_RT_GLB?$zoom$',
        f'https://images.asics.com/is/image/asics/{item_code}_{color_code}_SR_LT_GLB?$zoom$',
        f'https://images.asics.com/is/image/asics/{item_code}_{color_code}_SB_TP_GLB?$zoom$',
        f'https://images.asics.com/is/image/asics/{item_code}_{color_code}_SB_BT_GLB?$zoom$',
        f'https://images.asics.com/is/image/asics/{item_code}_{color_code}_SB_BK_GLB?$zoom$',
        f'https://images.asics.com/is/image/asics/{item_code}_{color_code}_SB_FR_GLB?$zoom$',
    ]
    return urls

def generate_saucony_image_urls(item_code: str, color_code: str):
    urls= [
        f'https://s7d4.scene7.com/is/image/WolverineWorldWide/{item_code}-{color_code}_1?$dw-hi-res$',
        f'https://s7d4.scene7.com/is/image/WolverineWorldWide/{item_code}-{color_code}_3?$dw-hi-res$',
        f'https://s7d4.scene7.com/is/image/WolverineWorldWide/{item_code}-{color_code}_5?$dw-hi-res$',
        f'https://s7d4.scene7.com/is/image/WolverineWorldWide/{item_code}-{color_code}_6?$dw-hi-res$',
        f'https://s7d4.scene7.com/is/image/WolverineWorldWide/{item_code}-{color_code}_4?$dw-hi-res$',
        f'https://s7d4.scene7.com/is/image/WolverineWorldWide/{item_code}-{color_code}_2?$dw-hi-res$',
    ]

    return urls

def generate_hoka_image_urls(item_code: str, color_code: str):
    urls = [
        f'https://dms.deckers.com/hoka/image/upload/q_auto,dpr_auto/b_rgb:ffffff/w_1610/v1701902246/{item_code}-{color_code}_1.png?_s=RAABAB0',
        f'https://dms.deckers.com/hoka/image/upload/q_auto,dpr_auto/b_rgb:ffffff/w_1610/v1701902246/{item_code}-{color_code}_8.png?_s=RAABAB0',
        f'https://dms.deckers.com/hoka/image/upload/q_auto,dpr_auto/b_rgb:ffffff/w_1610/v1701902246/{item_code}-{color_code}_2.png?_s=RAABAB0',
        f'https://dms.deckers.com/hoka/image/upload/q_auto,dpr_auto/b_rgb:ffffff/w_1610/v1701902246/{item_code}-{color_code}_7.png?_s=RAABAB0',
        f'https://dms.deckers.com/hoka/image/upload/q_auto,dpr_auto/b_rgb:ffffff/w_1610/v1701902246/{item_code}-{color_code}_5.png?_s=RAABAB0',
        f'https://dms.deckers.com/hoka/image/upload/q_auto,dpr_auto/b_rgb:ffffff/w_1610/v1701902246/{item_code}-{color_code}_6.png?_s=RAABAB0',
    ]

    return urls

if __name__ == "__main__":
    file_name = 'hoka2_export'

    REX_FILE_PATH = os.path.join(os.getcwd(), './hoka_rex.csv')
    SHOPIFY_FILE_PATH = os.path.join(os.getcwd(), f'./{file_name}.csv')

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
                product_code = get_product_code(description)
                item_code =product_code.split('-')[0]
                color_code = product_code.split("-")[1]
                urls = generate_hoka_image_urls(item_code, color_code)

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
