import pandas as pd

def read_file(file_path: str)-> pd.DataFrame:
    df = pd.read_csv(file_path, low_memory = False)
    return df

def filter_product_attributes(shopify_df : pd.DataFrame, rex_df: pd.DataFrame, columns : list[str], output_file_path: str):
    resultRows = []

    merged_df = pd.merge(shopify_df, rex_df[['SupplierSKU', 'SupplierSKU2']], left_on='Variant SKU', right_on='SupplierSKU', how='left')

    for index, row in merged_df.iterrows():
        currTitle = row['Title']
        barcode = str(row['Variant SKU'])
        status = row['Status']
        product_code = row['SupplierSKU2']
        brand = row['Vendor']
        published = row['Published']
        if pd.notna(currTitle):
            missing_columns = []
            for column in columns:
                if pd.isna(row[column]) or row[column] == "":

                    if column.strip().lower() == 'image src':
                        column = 'Images'
                    elif column.strip().lower() == "body (html)":
                        column = 'Description'
                    
                    missing_columns.append(column)

            if missing_columns:
                resultRows.append({
                    'Title' : currTitle,
                    'Barcode' : barcode,
                    'Missing Attributes' : ",".join(missing_columns),
                    'Brand' : brand,
                    'Status' : status,
                    'Published' : published
                })
                
        

    result_df = pd.DataFrame(resultRows)
    result_df.to_csv(output_file_path, index=False)

    shopify_df.to_csv('./drafted_export.csv')

    print(f'Done. The file has been written to {output_file_path}')



if __name__ == "__main__":

    shopify_df = read_file('./all_export.csv')
    rex_df = read_file('./rex_all.csv')

    filter_product_attributes(shopify_df, rex_df, ['Image Src', 'Body (HTML)'], 'missing_attributes.csv')
    print('Exiting...')