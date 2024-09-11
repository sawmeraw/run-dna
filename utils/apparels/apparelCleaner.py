import pandas as pd

def get_new_mansku(sku: str)-> str:
    index = sku.find('-')
    if index != -1:
        new_sku = sku[:index]
        return new_sku
    return sku

def replace_between_parentheses(description: str, replacement : str) -> str:
  start_index = description.find('(')
  end_index = description.find(')')

  if start_index != -1 and end_index != -1:
    to_replace = description[start_index+1: end_index]
    new_desc = description[:start_index + 1] + replacement + description[end_index:]

    return new_desc
  else:
    return description
  
def strip_color(desc: str) -> str:
   startIndex = desc.find(')')
   endIndex = desc.find('SZ')

   color = desc[startIndex +1 : endIndex].strip().title()
   return color

def _strip_brand_model(description: str) -> str:
    gender_prefix_map = {
        " M ": "Mens",
        " W ": "Womens",
        " K ": "Kids",
        " U ": "", 
        " B ": "Boys",
        " G ": "Girls"
    }

    stripped_description = description
    gender_label = ""

    for prefix, label in gender_prefix_map.items():
        if prefix in description:
            stripped_description = description.replace(prefix, " ")
            gender_label = label

    start_index = stripped_description.find('(')
    if start_index != -1:
        stripped_description = stripped_description[:start_index].strip()

    words = stripped_description.split()
    if words:
        last_word = words[-1]
        if gender_label:
            words[-1] = f"{gender_label} {last_word}"

    final_description = " ".join(words).lower().title()

    return final_description

def get_custom1(description: str, type: str):
   custom1 = ""
   first_part = _strip_brand_model(description=description)
   custom1 += first_part

   return custom1

if __name__ == "__main__":
    rexFile = './data/nike_app.csv'

    rex_df = pd.read_csv(rexFile, low_memory=False)

    for index, row in rex_df.iterrows():
        new_sku = get_new_mansku(row['ManufacturerSKU'])
        new_desc = replace_between_parentheses(row['ShortDescription'], row['ManufacturerSKU'])
        custom1 = get_custom1(row['ShortDescription'], row['ProductType'])
        color = strip_color(row['ShortDescription'])

        rex_df.at[index, 'Custom1'] = custom1
        rex_df.at[index, 'Colour'] = color
        rex_df.at[index, 'SupplierSKU2'] = row['ManufacturerSKU']
        rex_df.at[index, 'ShortDescription'] = new_desc
        rex_df.at[index, 'ManufacturerSKU'] = new_sku

    
    rex_df.to_csv('./results/nike_app_processed.csv', index=False)

    print('Done')


