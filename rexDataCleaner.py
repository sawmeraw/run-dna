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
  

def get_product_data(description, brands):

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
    
    if gender == 'M':
      product_name = f"{currBrand} {product_name} - Mens Running Shoes"
    elif gender == 'W':
      product_name = f"{currBrand} {product_name} - Womens Running Shoes"
    elif gender == 'U':
      product_name = f"{currBrand} {product_name} - Unisex Running Shoes"
    elif gender == 'K':
      product_name = f"{currBrand} {product_name} - Kids Running Shoes"



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


# brands = ["BROOKS", "NIKE"]
# description1 = "BROOKS M GHOST MAX 2 HELLO (038) BLACK/STEEL BLUE/CLOUD GREY SZ 7 (D)"
# description2 = "NIKE W AIR MAX (123) WHITE/BLACK/RED SZ 8 (B)"
# print(get_product_data(description1, brands))
# print(get_product_data(description2, brands))

brooksWidths = [ "A","D", "E", "X", "B"]
def process_brooks_mansku(sku):
  widIndex = -1
  found_width = None
  for width in brooksWidths:
    curr_index = sku.find(width)

    if curr_index != -1:
      widIndex= curr_index
      found_width = width
      break

  return widIndex, found_width

def process_dash_mansku(sku):
  widIndex = -1
  found_width = None
  if sku.find('-') != -1:
    widIndex = sku.find('-')
    found_width = True
  return widIndex, found_width 
  

if __name__ == "__main__":
  brands = ["BROOKS", "NIKE", "ASICS", "ADIDAS", "SAUCONY", "HOKA"]

  rexFile = pd.read_csv('./data/rex/nike_rex.csv')



  for index, row in rexFile.iterrows():
    rexFile.at[index, 'SupplierSKU2'] = row['ManufacturerSKU']
    product_name, custom2, color = get_product_data(row['ShortDescription'], brands)
    new_short_desc = replace_between_parentheses(row['ShortDescription'], row['ManufacturerSKU'])
    widIndex, found_width = process_dash_mansku(row['ManufacturerSKU'])
    if found_width:
      stripped_man_sku = row['ManufacturerSKU'][:widIndex]
    else:
      stripped_man_sku = row['ManufacturerSKU']
    rexFile.at[index, 'Custom1'] = product_name
    rexFile.at[index, 'ShortDescription'] = new_short_desc
    rexFile.at[index, 'ManufacturerSKU'] = stripped_man_sku
    rexFile.at[index, 'Custom2'] = custom2
    rexFile.at[index, 'Custom3'] = color
    rexFile.at[index, 'Colour'] = color
    
  rexFile.to_csv("./results/rex processed/nike_processed.csv", index=False)

  print('Done')