import pandas as pd
import os

file_name = 'misc1_export'

SHOPIFY_FILE_PATH = os.path.join(os.getcwd(), f'data/{file_name}.csv')
shopify_df = pd.read_csv(SHOPIFY_FILE_PATH)

#I dont even know what this does at this point, I kept adding logic until I got what I wanted
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


#https://cdn.shopify.com/s/files/1/0785/8765/8433/files/asics-glideride-max-mens-running-shoes-black-oatmeal-5.jpg?v=1725099131
def get_shopify_image_url(title, color, index):
    return f'https://cdn.shopify.com/s/files/1/0785/8765/8433/files/{title}-{color}-{index}.png?v=1725099131'


currTitle = ""

#first step is to add the Variant Image column with index set to 1 (genius logic lmao)
for index, row in shopify_df.iterrows():
    if not pd.isna(row['Title']):
        currTitle = row['Title']
    stripped_title = strip_title(currTitle)
    stripped_color = strip_color(row['Option2 Value'])

    shopify_image_url = get_shopify_image_url(stripped_title, stripped_color, 1)

    shopify_df.at[index, 'Variant Image'] = shopify_image_url


urlIndex = 0

#u dont wanna do the same thing twice
processed_combinations = set()
currTitle = ""


#second step is to add the rest of the images for the product, the pointer approach keeps track of product
# and its colors and helps to skip rows as well
for index, row in shopify_df.iterrows():
    title = row['Title']
    color = row['Option2 Value']

    # this fucker is important
    if pd.notna(title):
        urlIndex = index 
        currTitle = title

    combination_key = f"{currTitle}-{color}"
    

    if combination_key in processed_combinations:
        continue

    stripped_title = strip_title(currTitle)
    stripped_color = strip_color(color)


    for i in range(1, 7):
        image_url = get_shopify_image_url(stripped_title, stripped_color, i)
        if urlIndex < len(shopify_df):
            shopify_df.at[urlIndex, 'Image Src'] = image_url
            urlIndex += 1
        else:
            break 


    processed_combinations.add(combination_key)

output_file_path = f'ready to upload/{file_name}_with_images.csv'
shopify_df.to_csv(output_file_path, index=False)
    
print("Done. The file has been processed and saved with the Variant Image column updated.")

# blue expanse black
# sunrise red/true red
# white white
# white pale mint
#brooks-ghost-max-mens-running-shoes-crown