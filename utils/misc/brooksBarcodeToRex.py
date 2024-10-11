import pandas as pd


def read_file(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, low_memory=False)
    return df


def get_color(color_name_col: str) -> str:
   
    arr = color_name_col.split(' ')
    colors = arr[1:] if arr[1] else arr
    color_joined = " ".join(colors)
    #BLACK/BLACK/EBONY BLUE looks something like this right now
    color_split = color_joined.split('/')
    color_parts = []
    for word in color_split:
        if len(word.split(' ')) > 1:
            arr = word.split(' ')
            _word = " ".join(part.strip().capitalize() for part in arr)
        else:
            _word = word.capitalize()
        color_parts.append(_word.strip())
    return "/".join(color_parts)


def get_width_keyword(width_col: str)-> str:
    # Strips WIDTH D to D
    _line = width_col.lower().strip()
    _width = _line.replace("width", "")
    return _width.strip().upper()


def get_short_desc(product_name_col: str, product_code_col: str, color_name_col: str, color_code_col: str, size: str, width_col: str) -> str:
   
    brand = "BROOKS"
    color_arr = color_name_col.split(' ')
    _color = " ".join(color_arr[1:])
    _width = get_width_keyword(width_col)
    product_code = get_product_code(product_code_col=product_code_col, color_code_col=color_code_col, width_col=width_col)
    desc = brand + " " + product_name_col + " " + f"({product_code})" + " " + _color + " SZ " + size + " " + f"({_width})"
    return desc
   
def get_color_code(color_code_col: str)-> str:
    arr = color_code_col.split("_")
    return arr[2] if arr[2] else color_code_col


def get_product_code(product_code_col: str, color_code_col: str, width_col: str) -> str:
    color_code = get_color_code(color_code_col)
    width = get_width_keyword(width_col)
    keyword_map = {
        "2A":"A",
        "B":"B",
        "D":"D",
        "2E":"E",
        "4E":"X"
    }
   
    keyword = "F"
    if width in keyword_map:
        keyword = keyword_map[width]
   
    product_code = f"{product_code_col}{keyword}{color_code}"
    return product_code


def get_manufacturer_sku(full_product_code: str) -> str:
    index = -1
    for i in range(len(full_product_code)):
        if full_product_code[i].isupper():
            index = i
   
    return full_product_code[:index+1]


def get_model_name_with_gender(product_name_col: str)-> str:
    """Returns the model name with gender


    Args:
        product_name_col (str): M GHOST 16


    Returns:
        str: Ghost 16 - Mens
    """
    prefix_map = {
        'm' : "mens",
        "u": "unisex",
        "w": "womens",
    }
   
    misc_map = {
        "Gts" : "GTS",
        "Gtx": "GTX",
        "Se" : "SE"
    }
   
    parts = product_name_col.split(' ', 1)
    prefix = parts[0].strip().lower()
    name = parts[1].lower().strip().split(' ')
   
    gender_label = prefix_map.get(prefix, 'fixme')
    model = " ".join(word.strip().capitalize() for word in name)
    for key in misc_map.keys():
        if key in model:
            model = model.replace(key, misc_map.get(key))
    model_name = f"{model.strip()} - {gender_label.capitalize().strip()}"
    return model_name


def get_category(prod_group_col: str)-> str:
    _value = prod_group_col.strip().lower()
    category_map = {
        'racing/track': 'racing',
        'running': 'running',
        'trail' : 'trail running',
        "walking": 'walking'
    }
   
    category = None
    if _value in category_map:
        category = category_map.get(_value)
    else:
        category = "fixme"
   
    return category


def get_product_type(custom1: str ) -> str:
    index  = custom1.find('-')
    part = custom1[index+1:].strip()
   
    brac_index = part.find('(')
    product_type = part[:brac_index]
    return product_type.strip()
   


def get_custom1(prod_name_col: str, prod_group_col: str, width_col: str) -> str:
    brand = "Brooks"
    model_name = get_model_name_with_gender(product_name_col=prod_name_col)
    _width_part = width_col.replace('WIDTH', 'Width')
    category = get_category(prod_group_col=prod_group_col)
    custom1 = f"{brand} {model_name} {" ".join([word.capitalize() for word in category.split(" ")])} Shoes ({_width_part})"
    return custom1
   


def generate_rows(df: pd.DataFrame, output_file_path: str)-> str:
   
    df['Prod Code'] = df['Prod Code'].astype(str)
    df['Prod Name'] = df['Prod Name'].astype(str)
    df['Clr Code'] = df['Clr Code'].astype(str)
    df['Clr Name'] = df['Clr Name'].astype(str)
    df['SKU Size'] = df['SKU Size'].astype(str)
    df['SKU Barcode'] = df['SKU Barcode'].astype(str)
    df['Model Number'] = df['Model Number'].astype(str)
    df['Product Group'] = df['Product Group'].astype(str)
    df['Gender'] = df['Gender'].astype(str)
   
    columns = [
    'ProductId',
    'ManufacturerSKU',
    'SupplierSKU',
    'ShortDescription',
    'Size',
    'Colour',
    'Season',
    'Custom1',
    'Custom2',
    'Custom3',
    'SupplierBuy',
    'BuyPriceEx',
    'DirectCosts',
    'RRP',
    'POSPriceMarkupTarget',
    'POSPrice',
    'WebPrice',
    'DiscountPrice',
    'DiscountEnd',
    'ProductType',
    'WebstoreMenuID',
    'LongDescription',
    'WarrantyDetails',
    'LeadTime',
    'CartonQty',
    'CoreProduct',
    'Manufacturer',
    'Brand',
    'SupplierCode',
    'Length',
    'Depth',
    'Breadth',
    'ShippingCubic',
    'Weight',
    'Freight',
    'RequiresAssembly',
    'Disabled',
    'ExportToWebService',
    'Attribute:Specials',
    'Attribute:Width',
    'Channel:Default Channel',
    'Channel:StoreA',
    'Publish To:rundna-au.myshopify.com',
    'SupplierSKU2',
    'Prevent Disabled',
    'DateLastSold',
    'DateLastFulfiled'
    ]
   
    rex_df = pd.DataFrame(columns=columns)
   
    data = []
   
    for index, fileRow in df.iterrows():
        print(index)
        full_product_code = get_product_code(fileRow['Prod Code'], fileRow['Clr Code'], fileRow['Model Number'])
        color_name = get_color(fileRow['Clr Name'])
        man_sku = get_manufacturer_sku(full_product_code=full_product_code)
        size = fileRow['SKU Size']
        barcode = fileRow['SKU Barcode']
        brand = "BROOKS"
        publish = 'True'
        supplier_code = "BR"
        custom1 = get_custom1(fileRow['Prod Name'], fileRow['Product Group'], fileRow['Model Number'])
        prod_type = get_product_type(custom1=custom1)
        short_desc = get_short_desc(fileRow['Prod Name'], fileRow['Prod Code'], fileRow['Clr Name'], fileRow['Clr Code'], fileRow['SKU Size'], fileRow['Model Number'] )
       
        row = {
            'ManufacturerSKU' : man_sku,
            'SupplierSKU' : barcode,
            'ShortDescription': short_desc,
            'Size' : size,
            'Colour': color_name,
            'Custom1': custom1,
            'ProductType': prod_type,
            'Brand': brand,
            'SupplierCode': supplier_code,
            'SupplierSKU2': full_product_code,
            'Publish To:rundna-au.myshopify.com': publish,
           
        }
       
        data.append(row)
   
    for row in data:
        rex_df = rex_df._append(row, ignore_index = True)
   
    rex_df = rex_df.fillna("")
    rex_df.to_csv(output_file_path, index=False)
    print(f'File written to {output_file_path}')
   


def check_exceeding_manskus(df: pd.DataFrame):
    unique_counts = df['ManufacturerSKU'].value_counts()
    pd.set_option('display.max_rows', None)
    print(unique_counts)


if __name__ == "__main__":
   
    barcode_df = read_file('./barcodes.csv')
    rex_df = read_file('./rex_file.csv')
   
    # generate_rows(barcode_df, output_file_path="rex_file.csv")
    # print(get_product_type('Brooks Ghost 16 - Mens Trail Running Shoes (Width D)'))
    check_exceeding_manskus(rex_df)
    print("Exiting...")
