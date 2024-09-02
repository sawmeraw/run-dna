import pandas as pd
import os

REX_FILE_PATH = os.path.join(os.getcwd(), 'data/asics_rex.csv')
SHOPIFY_FILE_PATH = os.path.join(os.getcwd(), 'data/products_export.csv')

rex_df = pd.read_csv(REX_FILE_PATH)
shopify_df = pd.read_csv(SHOPIFY_FILE_PATH)

def clean_barcode(barcode):
    return barcode.replace("'", "")

def get_product_code(description):
    startIndex = description.find("(")
    endIndex = description.find(")")
    return description[startIndex+1:endIndex]


def generate_asics_image_urls(product_code : str):
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

product_codes_processed = set()

urlIndex = 0

for index, row in shopify_df.iterrows():

    if not pd.isna(row['Title']):
        urlIndex = index
    
    barcode = clean_barcode(row['Variant SKU'])

    for _, rex_row in rex_df.iterrows():
        if barcode in rex_row['SupplierSKU']:
            description = rex_row['ShortDescription']
            product_code = get_product_code(description)
            if product_code in product_codes_processed:
                continue

            product_codes_processed.add(product_code)
            urls = generate_asics_image_urls(product_code)
            
            for i, url in enumerate(urls):
                if urlIndex + i < len(shopify_df):
                    shopify_df.at[urlIndex + i, 'Image Src'] = url
                else:
                    
                    break
            
            urlIndex += len(urls)
            break

shopify_df = shopify_df.sort_values(by=['Title', 'Option2 Value'])
shopify_df.to_csv(os.path.join(os.getcwd(), 'data/product_export_processed.csv'), index=False)

print("Done")
