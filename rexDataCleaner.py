import re
import pandas as pd

def capitalize_color_part(part):
  return ' '.join(word.capitalize() for word in part.split())

def format_color(color):
  color = color.replace('-', '/')
  return '/'.join(capitalize_color_part(part) for part in color.split('/'))

def replace_between_parentheses(description, replacement):
  start_index = description.find('(')
  end_index = description.find(')')

  if start_index != -1 and end_index != -1:
    to_replace = description[start_index+1: end_index]
    new_desc = description[:start_index + 1] + replacement + description[end_index:]

    return new_desc
  else:
    return description
  

def get_product_data(description, brands, type):

  product_name = ""
  width = ""
  color = ""
  custom2 = ""
  currBrand = ""
  currGender = ""


  gender_width_match = re.search(r'\b(M|W|U)\b.*?\s+(\w{1,2})\s*\(', description)
  if gender_width_match:
      gender = gender_width_match.group(1)
      width = gender_width_match.group(2)
      currGender = gender
  else:
      gender = ''

  

  for brand in brands:
    if brand in description:
      currBrand = brand.lower().capitalize()
      start_index = description.find(f"{brand} {gender}") + len(
          f"{brand} {gender}")
      end_index = description.find("(", start_index)
      if end_index != -1:
        product_name = description[start_index:end_index].strip()
      break


  split_model = product_name.split(" ")
  for word in split_model:
    product_name = product_name.replace(word, word.lower().capitalize())

  

  if len(split_model) > 1:
    category = "Running Shoes"
    if type.find('Athletics') != -1:
      category = "Track & Field Shoes"
    elif type.find('Racing') != -1:
      category = "Racing Shoes"
    elif type.find('Trail') != -1:
      category = "Trail Running Shoes"
    


    if gender == 'M':
      product_name = f"{currBrand} {product_name} - Mens {category}"
    elif gender == 'W':
      product_name = f"{currBrand} {product_name} - Womens {category}"
    elif gender == 'U':
      product_name = f"{currBrand} {product_name} - Unisex {category}"
    elif gender == 'K':
      product_name = f"{currBrand} {product_name} - Kids {category}"



  width_match = re.search(r'\((\w{1,2})\)', description)
  if width_match:
    width = width_match.group(1)
    


  color_match = re.search(r'\)\s*(.*?)\s+SZ', description)
  if color_match:
    color = color_match.group(1).strip()
    
    color = format_color(color)

  
  if gender == 'M':
    if width == 'D':
      custom2 = 'D - Mens Standard'
    elif width == '2E':
      custom2 = '2E - Mens Wide'
    elif width == '4E':
      custom2 = '4E - Mens Extra-Wide'
    elif width == 'B':
      custom2 = 'B - Mens Narrow'
  elif gender == 'W':
    if width == '2A':
      custom2 = '2A - Womens Narrow'
    elif width == 'B':
      custom2 = 'B - Womens Standard'
    elif width == 'D':
      custom2 = 'D - Womens Wide'
    elif width == '2E':
      custom2 = '2E - Womens Extra-Wide'
  elif gender == 'U':
    custom2 = 'D - Mens Standard'

  product_name += f" (Width{' '}{width})"
  
  return product_name, custom2, color


#3WD30121197
def process_dash_mansku(sku):
  widIndex = -1
  found_width = None
  if sku.find('-') != -1:
    widIndex = sku.find('-')
    found_width = True
  return widIndex, found_width

def process_index_mansku(sku):
  return 8, True
  

if __name__ == "__main__":
  brands = ["BROOKS", "NIKE", "ASICS", "ADIDAS", "SAUCONY", "NEW BALANCE", "HOKA", "ON RUNNING", "ON", "VIVOBAREFOOT", "PUMA", "ALTRA"]

  rexFile = pd.read_csv('./data/rex/nb_rex.csv')

  for index, row in rexFile.iterrows():
    rexFile.at[index, 'SupplierSKU2'] = row['ManufacturerSKU']
    product_name, custom2, color = get_product_data(row['ShortDescription'], brands, row['ProductType'])
    new_short_desc = replace_between_parentheses(row['ShortDescription'], row['ManufacturerSKU'])
    # widIndex, found_width = process_index_mansku(row['ManufacturerSKU'])
    # if found_width:
    #   stripped_man_sku = row['ManufacturerSKU'][:widIndex]
    # else:
    #   stripped_man_sku = row['ManufacturerSKU']
    rexFile.at[index, 'Custom1'] = product_name
    rexFile.at[index, 'ShortDescription'] = new_short_desc
    # rexFile.at[index, 'ManufacturerSKU'] = stripped_man_sku
    rexFile.at[index, 'Custom2'] = custom2
    rexFile.at[index, 'Colour'] = color
    
    
    
  rexFile.to_csv("./results/rex processed/nb_processed.csv", index=False)

  print('Done')