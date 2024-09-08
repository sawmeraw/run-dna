import re
import pandas as pd

# Helper functions
def capitalize_color_part(part:str):
    return ' '.join(word.capitalize() for word in part.split())

def format_color(color: str):
    color = color.replace('-', '/')
    return '/'.join(capitalize_color_part(part) for part in color.split('/'))

def replace_between_parentheses(description:str, replacement:str):
    start_index = description.find('(')
    end_index = description.find(')')

    if start_index != -1 and end_index != -1:
        new_desc = description[:start_index + 1] + replacement + description[end_index:]
        return new_desc
    else:
        return description


# New function to get product name (Custom1)
def get_custom1(description: str, brands, product_type: str):
    # Match gender and width (e.g., M, W, U, etc.)
    gender_width_match = re.search(r'\b(M|W|U)\b.*?\s+(\w{1,2})\s*\(', description)
    gender = gender_width_match.group(1) if gender_width_match else ''
    width_match = re.search(r'\((\w{1,2})\)', description)
    width = width_match.group(1) if width_match else ''

    curr_brand, product_name = '', ''
    
    for brand in brands:
        if brand.strip().lower() in description.lower():
            curr_brand = brand.strip().lower().title()

            start_index = description.lower().find(f"{brand.lower()} {gender.lower()}") + len(f"{brand} {gender}")
            end_index = description.find("(", start_index)
            if end_index != -1:
                product_name = description[start_index:end_index].strip()
            break

    product_name = ' '.join([word.capitalize() for word in product_name.split()])

    category = get_category(product_type)

    if gender == 'M':
        product_name = f"{curr_brand.strip()} {product_name} - Mens {category} (Width {width})"
    elif gender == 'W':
        product_name = f"{curr_brand.strip()} {product_name} - Womens {category} (Width {width})"
    elif gender == 'U':
        product_name = f"{curr_brand.strip()} {product_name} - Unisex {category} (Width {width})"
    elif gender == 'K':
        product_name = f"{curr_brand.strip()} {product_name} - Kids {category} (Width {width})"

    return product_name

# Function to get the category based on product type
def get_category(product_type : str):
    if 'Athletics' in product_type:
        return "Track & Field Shoes"
    elif 'Racing' in product_type:
        return "Racing Shoes"
    elif 'Trail' in product_type:
        return "Trail Running Shoes"
    else:
        return "Running Shoes"

# Function to extract color
def get_color(description):
    color_match = re.search(r'\)\s*(.*?)\s+SZ', description)
    if color_match:
        color = color_match.group(1).strip()
        color = format_color(color)
        return color
    return ""

def get_new_desc(description, manufacturer_sku):
    return replace_between_parentheses(description, manufacturer_sku)


def get_new_mansku(sku: str, brand: str) -> str:
    _brand = brand.lower().strip()

    if _brand == "asics":
        return process_asics_mansku(sku)
    elif _brand == "brooks":
        return process_brooks_mansku(sku)
    elif _brand == "new balance":
        return process_new_balance_mansku(sku)
    elif _brand in ["vivobarefoot", "hoka", "saucony", "merrell", "puma", "nike"]:
        return process_shared_logic_mansku(sku)  # Shared logic
    elif _brand == "mizuno":
        return process_mizuno_mansku(sku)
    elif _brand == "on running":
        return process_on_running_mansku(sku)
    elif _brand == "altra":
        return process_altra_mansku(sku)
    else:
        return sku  # Default: return the SKU unmodified if brand is not recognized

# Shared logic function for Hoka, Saucony, Vivobarefoot, Merrell, Puma
def process_shared_logic_mansku(sku: str) -> str:
    index = sku.find("-")
    return sku[:index]

def process_asics_mansku(sku: str) -> str:
    startIndex = sku.find(".")
    return sku[:startIndex]

def process_brooks_mansku(sku: str) -> str:
    widths = ['A', 'B', 'D', 'E', 'X']
    for width in widths:
        if sku.find(width) != -1:
            index = sku.find(width)
            item_code = sku[:index+1]
            return item_code
    
    return sku

def process_new_balance_mansku(sku: str) -> str:
    return sku

def process_mizuno_mansku(sku: str) -> str:
    return sku[:-2]

def process_on_running_mansku(sku: str) -> str:
    return sku[:sku.find('.') + 3] if '.' in sku else sku[:8]

def process_altra_mansku(sku: str) -> str:
    return sku[:-3]


if __name__ == "__main__":

    # Load CSV
    rexFile = pd.read_csv('./data/22_23_run_rem_stock_filtered.csv', low_memory=False)

    brands = rexFile['Brand'].unique().tolist()

    for index, row in rexFile.iterrows():
        # Extract
        description = row['ShortDescription']
        product_type = row['ProductType']
        manufacturer_sku = row['ManufacturerSKU']
        currBrand = row['Brand']

        # Process
        product_name = get_custom1(description, brands, product_type)
        color = get_color(description)
        new_short_desc = get_new_desc(description, manufacturer_sku)
        new_mansku= get_new_mansku(manufacturer_sku, currBrand)

        # Update
        rexFile.at[index, 'SupplierSKU2'] = manufacturer_sku
        rexFile.at[index, 'Custom1'] = product_name
        rexFile.at[index, 'ShortDescription'] = new_short_desc
        rexFile.at[index, 'Colour'] = color
        rexFile.at[index, 'ManufacturerSKU'] = new_mansku

    rexFile.to_csv("./results/22_23_run_rem_processed.csv", index=False)

    print('Done')
