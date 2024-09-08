import pandas as pd
import os
import re

def get_width(mansku : str)-> str:
    return mansku.split("-")[-1]

#NEW BALANCE M FRESH FOAM X 1080V13 (A) WHITE/BLACK/COASTAL BLUE/GINGER LEMON SZ 7 (D)

def get_custom1(brand: str, mansku: str, desc: str, type: str) -> str:
    width = get_width(mansku)

    category = "Running Shoes"
    if type.find('Athletics') != -1:
      category = "Track & Field Shoes"
    elif type.find('Racing') != -1:
      category = "Racing Shoes"
    elif type.find('Trail') != -1:
      category = "Trail Running Shoes"

    startIndex = desc.find('(')
    first_part = desc[:startIndex]
    
    arr = first_part.split(" ")

    custom1 = brand + " "
    for index, word in enumerate(arr):
       if index <=2:
        continue
       custom1 += word.lower().title() + " "

    gender = ""
    if type.find("-M-") != -1:
       gender = "Mens"
    elif type.find('-W-') != -1:
       gender = "Womens"
    elif type.find("-U-") != -1:
       gender = "Unisex"
    
    product_name = f"{custom1.strip()} - {gender.strip()} {category.strip()} (Width {width})"

    return product_name 

def get_new_short_description (desc: str, mansku: str) -> str:
    start_index = desc.find('(')
    end_index = desc.find(')')

    if start_index != -1 and end_index != -1:
        to_replace = desc[start_index+1: end_index]
        new_desc = desc[:start_index + 1] + mansku + desc[end_index:]

        return new_desc
    else:
        return desc
    
def get_new_mansku(sku: str)-> str:
    models = ["1080V13", "1080V14", "860V14", "860V13", "880V14", "880V13", "680V8", "RCELV4", "RCXV3", "THEIRV8", "THEIRV7"]
    pattern = r'(\d{3,4})([A-Z]?)(\d{2})'

    # Search for the pattern in the SKU
    match = re.search(pattern, sku)
    if match:
        # Extract the key parts: model number and version
        model_num = match.group(1) + "V" + match.group(3)
        
        # Check if the model_num with 'V' fits one of the known models
        for model in models:
            if model_num == model:
                # Replace the middle part of the SKU with the correct model
                new_sku = re.sub(pattern, model, sku)
                return new_sku
            else:
               return sku

def strip_color(desc: str) -> str:
   startIndex = desc.find(')')
   endIndex = desc.find('SZ')

   color = desc[startIndex +1 : endIndex].strip().title()
   return color

if __name__ == "__main__":
    brand = "New Balance"
    REX_FILE_PATH = f'results/rex processed/nb_processed.csv'
    rex_df = pd.read_csv(REX_FILE_PATH)

    for index, row in rex_df.iterrows():
       color = strip_color(row['ShortDescription'])
       rex_df.at[index, 'Colour'] = color
    #    rex_df.at[index, 'SupplierSKU2'] = row['ManufacturerSKU']
    #    rex_df.at[index, 'Custom1'] = get_custom1(brand, row['ManufacturerSKU'], row['ShortDescription'], row['ProductType'])
    #    new_desc = get_new_short_description(row["ShortDescription"], row["ManufacturerSKU"])
    #    rex_df.at[index, 'ShortDescription'] = new_desc

    #    new_sku = get_new_mansku(row["ManufacturerSKU"])
    #    rex_df.at[index, 'ManufacturerSKU'] = new_sku

       

    rex_df.to_csv(f'./results/rex processed/nb_processed_colors.csv', index=False)
    print('Done')