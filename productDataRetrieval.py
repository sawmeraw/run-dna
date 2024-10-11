import pandas as pd


def read_file(file_path: str)-> pd.DataFrame:
    df = pd.read_csv(file_path, low_memory=False)
    return df




def count_non_empty_fields(data: dict)-> int:
    return sum(1 for value in data.values() if value)




def write_data_to_csv(data: dict, file_path: str):
    rows = []
   
    def fill_missing_fields(primary_fields: dict, secondary_fields: dict):
        for key in ['description', 'cushioning', 'support', 'best_for']:
            if not primary_fields.get(key) or primary_fields[key] == 'nan':
                primary_fields[key] = secondary_fields.get(key, '')
        return primary_fields
   
    def clean_value(value):
        return '' if pd.isna(value) or value == 'nan' else value
   
    for title, gender_data in data.items():
        if title == "nan":
            continue
       
        mens_data = gender_data.get('Mens', {})
        womens_data = gender_data.get('Womens', {})
        unisex_data = gender_data.get('Unisex', {})


        if womens_data and mens_data:
            womens_data = fill_missing_fields(womens_data, mens_data)
        elif mens_data and not womens_data:
            womens_data = mens_data
       
        if mens_data and womens_data:
            mens_data = fill_missing_fields(mens_data, womens_data)
        elif womens_data and not mens_data:
            mens_data = womens_data
       
        if unisex_data:
            unisex_data = fill_missing_fields(unisex_data, mens_data if mens_data else womens_data)
        elif not unisex_data:
            unisex_data = mens_data if mens_data else womens_data


        for gender, fields in {'Mens': mens_data, 'Womens': womens_data, 'Unisex': unisex_data}.items():
            if fields:
                row = {
                    'Title': title,
                    'Gender': gender,
                    'Description': clean_value(fields.get('description', '')),
                    'Cushioning': clean_value(fields.get('cushioning', '')),
                    'Drop': clean_value(fields.get('drop', '')),
                    'Heel Stack': clean_value(fields.get('heel_stack', '')),
                    'Support': clean_value(fields.get('support', '')),
                    'Best For': clean_value(fields.get('best_for', '')),
                    'Weight': clean_value(fields.get('weight', ''))
                }
                rows.append(row)
   
    flat_df = pd.DataFrame(rows)
    flat_df.to_csv(file_path, index=False)
    print(f"Data written to {file_path}")
   
def merge_files(shopify_df: pd.DataFrame, rex_df: pd.DataFrame, stock_df: pd.DataFrame)-> pd.DataFrame:
   
    product_code_merged_df = pd.merge(shopify_df, rex_df[['SupplierSKU', 'SupplierSKU2']], left_on='Variant SKU', right_on='SupplierSKU', how='left')
   
    stock_merged_df = pd.merge(product_code_merged_df, stock_df[['Inventory', 'ShortDescription', 'SupplierSKU', 'Publish To:rundna-au.myshopify.com']], left_on='Variant SKU', right_on='SupplierSKU', how='left')
   
    stock_merged_df = stock_merged_df.drop(columns=['SupplierSKU_x', 'SupplierSKU_y'])
    # stock_merged_df.to_csv('./test_merge.csv', index=False)
    return stock_merged_df
   


def get_footwear_data(df: pd.DataFrame)-> dict:
   
    products = {}
   
    columns_to_convert = [
        'Title',
        'Body (HTML)',
        'Gender (product.metafields.product.gender)',
        'Cushioning (product.metafields.productspecs.cushioning)',
        'Drop (product.metafields.productspecs.drop)',
        'Heel Stack (product.metafields.productspecs.heel_stack)',
        'Support (product.metafields.productspecs.support)',
        'Best For (product.metafields.productspecs.surface)',
        'Weight (product.metafields.productspecs.weight)',
        'Type'
    ]


    # Convert specified columns to string
    df[columns_to_convert] = df[columns_to_convert].astype(str)
   
    for index, row in df.iterrows():
        title = row['Title']
        product_type = str(row['Type'])
        _title = title.split('- ')[0]
        if not pd.isna(_title) and _title:
            if "shoes" in product_type.strip().lower():
               
                description = row['Body (HTML)'] if pd.notna(row['Body (HTML)']) else ""
                gender = row['Gender (product.metafields.product.gender)'] if pd.notna(row['Gender (product.metafields.product.gender)']) else ""
                cushioning = row['Cushioning (product.metafields.productspecs.cushioning)'] if pd.notna(row['Cushioning (product.metafields.productspecs.cushioning)']) else ""
                drop = row['Drop (product.metafields.productspecs.drop)'] if pd.notna(row['Drop (product.metafields.productspecs.drop)']) else ""
                heel_stack = row['Heel Stack (product.metafields.productspecs.heel_stack)'] if pd.notna(row['Heel Stack (product.metafields.productspecs.heel_stack)']) else ""
                support = row['Support (product.metafields.productspecs.support)'] if pd.notna(row['Support (product.metafields.productspecs.support)']) else ""
                best_for = row['Best For (product.metafields.productspecs.surface)'] if pd.notna(row['Best For (product.metafields.productspecs.surface)']) else ""
                weight = row['Weight (product.metafields.productspecs.weight)'] if pd.notna(row['Weight (product.metafields.productspecs.weight)']) else ""
               
                product_data = {
                    'description': description,
                    'cushioning': cushioning,
                    'drop': drop,
                    'heel_stack': heel_stack,
                    'support': support,
                    'best_for': best_for,
                    'weight': weight
                }
               
                if _title not in products:
                    products[_title] = {}
               
                if gender and gender not in products[_title]:
                    products[_title][gender] = {}
               
                if gender and (not products[_title][gender] or count_non_empty_fields(product_data) > count_non_empty_fields(products[_title][gender])):
                    products[_title][gender] = product_data
           
        else:
            continue
   
    return products


#not sure why asics apparel stock count was wrong with this script
def filter_product_attributes(df: pd.DataFrame, columns: list[str], output_file_path: str):
    resultRows = []
    current_title = None
    stock_count = 0
    published_to_rex = True
    current_data = None  # To temporarily hold the current row's data for output later

    for index, row in df.iterrows():
        currTitle = row['Title']
        barcode = str(row['Variant SKU'])
        brand = row['Vendor']
        status = row['Status']
        product_code = row['SupplierSKU2']  #merged column
        product_type = str(row['Type'])


        inventory = row['Inventory'] if pd.notna(row['Inventory']) else 0  # Handle Inventory

        # If we encounter a new title
        if pd.notna(currTitle) and currTitle != current_title and "shoes" not in product_type.lower().strip():
           
            if current_title is not None:
               
                current_data['In Stock?'] = f"Yes ({int(stock_count)})" if stock_count > 0 else "No"
                current_data['Published in REX'] = "True" if published_to_rex else "False"
                resultRows.append(current_data)


            current_title = currTitle
            stock_count = 0
            current_data = None


        stock_count += inventory
        published_to_rex = row['Publish To:rundna-au.myshopify.com']

        if current_data is None:
            missing_columns = []
            for column in columns:
                if pd.isna(row[column]) or row[column] == "":
                    if column.strip().lower() == "image src":
                        column = 'Images'
                    elif column.strip().lower() == 'body (html)':
                        column = 'Description'
                    missing_columns.append(column)

            current_data = {
                'Title': currTitle,
                'Barcode': barcode,
                'Missing Attributes': ",".join(missing_columns),
                'Brand' : brand,
                'Status': status,
                'Product Type': product_type,
                'Product Code in REX': product_code if pd.notna(product_code) else 'Not found',
                'In Stock?': "No",
                'Published in REX': published_to_rex
            }
    
    if current_data:
        current_data['In Stock?'] = f"Yes ({stock_count})" if stock_count > 0 else "No"
        resultRows.append(current_data)

    result_df = pd.DataFrame(resultRows)
    result_df.to_csv(output_file_path, index=False)


    print(f'Done. The file has been written to {output_file_path}')



if __name__ == "__main__":
   
    shopify_df = read_file('./all_export.csv')
    rex_df = read_file('./rex_all.csv')
    stock_df = read_file('./stock_file.csv')
    
    merged_df = merge_files(shopify_df=shopify_df, rex_df=rex_df, stock_df=stock_df)
    
    filter_product_attributes(merged_df, ['Image Src', 'Body (HTML)', 'Variant Image'], 'acc_and_app.csv')
    
    # write_data_to_csv(data, 'shopify_product_data.csv')
    
    # merged_df.to_csv('./testmerge.csv', index=False)
    
    print('Done')


