import pandas as pd


def get_season_from_month(month_col: str) -> str:
    season_map = {
        'DEC': "24-Q4",
        'JAN': "25-Q1",
        'FEB': "25-Q1",
        'MAR': "25-Q1",
        'APR': "25-Q2",
    }
   
    _month = month_col.strip()
    season = None
    if _month in season_map:
        season = season_map.get(_month)
        return season
    return month_col


def read_file(file_path: str)-> pd.DataFrame:
    df = pd.read_csv(file_path, low_memory=False)
    return df


def strip_mansku(sku: str) -> str:
    # print(f"Original SKU: {sku}")
    if '.' in sku:
        result = sku[:sku.find('.')]
        # print(f"Stripped SKU: {result}")
        return result
    print(f"No dot found in SKU. Returning full SKU: {sku}")
    return sku

def get_color(color_name_col: str) -> str:
    
    #BLACK/BLACK/EBONY BLUE looks something like this right now
    color_split = color_name_col.split('/')
    color_parts = []
    for word in color_split:
        if len(word.split(' ')) > 1:
            arr = word.split(' ')
            _word = " ".join(part.strip().capitalize() for part in arr)
        else:
            _word = word.capitalize()
        color_parts.append(_word.strip())
    return "/".join(color_parts)

def get_short_desc(desc_col: str, trading_code_col: str, color_col: str, size_col: str, gender_col: str, width_col: str):
    brand = "ASICS"
    keyword_map = {
        "kids":"K", 
        "unisex":"U",
        "women":"W",
        "men":"M"
    }

    _gender_col = gender_col.strip().lower()
    if _gender_col in keyword_map:
        gender_keyword = keyword_map.get(_gender_col, _gender_col)

    brac_index = desc_col.find('(')
    if brac_index != -1:
        _model = desc_col[:brac_index]
    else:
        _model = desc_col.strip()

    _width = ""
    if _gender_col != "kids":
        _width = f'({width_col})'
    
    custom1 = f'{brand} {gender_keyword} {_model} ({trading_code_col}) {color_col} SZ {size_col} {_width}'

    return custom1
    
def get_custom1():
    
    return None

def map_and_sort_data(df: pd.DataFrame, output_file_path: str) -> str:
    size_map = {
        '4H':'4.5',
        '5H':'5.5',
        '6H':'6.5',
        '7H':'7.5',
        '8H':'8.5',
        '9H':'9.5',
        '10H':'10.5',
        '11H':'11.5',
        '12H':'12.5',
        '13H':'13.5',
        '14H':'14.5',
    }
   
    standard_width_map = {
        'Men' : "D",
        'Women': "B",
        "Unisex": "D"
    }
   
    df['Width'] = df['Width'].fillna("")
    df['Width'] = df['Width'].astype(str)
    df['AOP Gender'] = df['AOP Gender'].astype(str)
    df['Retail'] = df['Retail'].astype(str)
    df['Size'] = df['Size'].astype(str)
    df['Trading Code'] = df['Trading Code'].astype(str)
    df['Price'] = df['Price'].astype(str)
    df['ManufacturerSKU'] = ""
    df['Season'] = ""
    df['Color (REX)'] = ""
    df['ShortDescription'] = ""
    for index, row in df.iterrows():
        # print(index)
        gender = row['AOP Gender']
        width = row['Width']
        retail_price = str(row['Retail']).replace('$', '').strip()
        cost_price = str(row['Price']).replace('$', '').strip()
        rrp = float(retail_price)
        size = row['Size']
        product_code = str(row['Trading Code'])
        season = get_season_from_month(str(row['INTRO MONTH']))
        rex_color = get_color(str(row['Colour']))
        if pd.isna(product_code) or product_code == "":
            print(f'Product code is empty at index {index}')
           
        man_sku = strip_mansku(product_code)
       
        if man_sku == "":
            print(f"Skipping index {index}: Manufacturer SKU is empty after stripping")
       
       
        if size in size_map:
            df.at[index, 'Size'] = size_map.get(size)
       
        df.at[index, 'Retail'] = rrp - 0.01
        df.at[index, 'ManufacturerSKU'] = man_sku
        df.at[index, 'Season'] = season
        df.at[index, 'Color (REX)'] = rex_color
        df.at[index, 'Price'] = cost_price
        _width_for_short_desc = ""
        if width == "":
            _gender = gender.strip()
            if _gender in standard_width_map:
                _width_for_short_desc = standard_width_map[_gender]
                df.at[index, 'Width'] = _width_for_short_desc
        else:
            _width_for_short_desc = row['Width']

        short_desc = get_short_desc(row['Description'], row['Trading Code'], row['Colour'], row['Size'], row['AOP Gender'], _width_for_short_desc)
        df.at[index, 'ShortDescription'] = short_desc

                
           
           
    df.to_csv(output_file_path, index=False)
    print(f'File written to {output_file_path}')
               
if __name__=="__main__":
    df = read_file("./asics.csv")
   
    # write_variant_barcode(df, output_file_path="sku_upload_result.csv")%~
    map_and_sort_data(df, 'asics_size_fix.csv')
    
    print('Exiting...')