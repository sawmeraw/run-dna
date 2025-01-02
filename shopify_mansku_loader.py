import pandas as pd

def find_changed_columns(file1: str, file2: str, key_column: str):
    """
    Compares two CSV files and prints the names of columns with changes.

    :param file1: Path to the first CSV file.
    :param file2: Path to the second CSV file.
    :param key_column: Column name that serves as the unique key for comparison.
    """
    df1 = pd.read_csv(file1, dtype=str)
    df2 = pd.read_csv(file2, dtype=str)

    df1.fillna("", inplace=True)
    df2.fillna("", inplace=True)

    # Ensure the key column exists in both files
    if key_column not in df1.columns or key_column not in df2.columns:
        raise ValueError(f"The key column '{key_column}' must exist in both CSV files.")
    
    df1.set_index(key_column, inplace=True)
    df2.set_index(key_column, inplace=True)

    changed_columns = []
    for column in df1.columns:
        if not df1[column].equals(df2[column]):
            changed_columns.append(column)

    if changed_columns:
        print("Columns with changes detected:")
        print(", ".join(changed_columns))
    else:
        print("No changes detected in any column.")

def readFile(path: str, col = False) -> pd.DataFrame:
    if col:
        df = pd.read_csv(path, low_memory=False, dtype=str)
    else:
        df = pd.read_csv(path, low_memory = False, dtype = str)
    return df

def writeMansku(rex_df: pd.DataFrame, shopify_df: pd.DataFrame, outFileName: str, minLengthForMansku: int):
    shopify_df['ManufacturerSKU (product.metafields.custom.manufacturersku)'] = shopify_df['ManufacturerSKU (product.metafields.custom.manufacturersku)'].apply(lambda x: str(x) if pd.notna(x) else "")

    for index, row in shopify_df.iterrows():
        if pd.notna(row['Title']):
            _barcode = str(row['Variant SKU'])
            barcode = _barcode.replace("'", "") if "'" in _barcode else _barcode
            
            for rexIndex, rexRow in rex_df.iterrows():
                supplierSku = str(rexRow['SupplierSKU'])
                if supplierSku == barcode:
                    mansku = rexRow['ManufacturerSKU']
                    if len(mansku) != minLengthForMansku: 
                        mansku = rexRow['SupplierSKU2']

                    if mansku:
                        shopify_df.at[index, 'ManufacturerSKU (product.metafields.custom.manufacturersku)'] = mansku
                    else:
                        shopify_df.at[index, 'ManufacturerSKU (product.metafields.custom.manufacturersku)'] = ""
                    shopify_df.at[index, 'Included / Europe + others'] = 'FALSE'
                    shopify_df.at[index, 'Included / New Zealand'] = 'FALSE'



    shopify_df.drop(['Image Src', 'Image Position', 'Variant Image'], axis=1, inplace=True)

    # Write the updated dataframe to CSV
    shopify_df.to_csv(f"{outFileName}", index=False, float_format='%s')
    print(f"File written to {outFileName}")


if __name__ == "__main__":
    SHOPIFY_FILE = 'kayano_test.csv'
    OUT_FILE_NAME = 'kayano_result.csv'
    REX_FILE = 'asics_rex.csv'

    shopify_df = readFile(SHOPIFY_FILE)
    rex_df = readFile(REX_FILE, True)
    writeMansku(rex_df=rex_df, shopify_df=shopify_df, outFileName=OUT_FILE_NAME, minLengthForMansku=12)

    # find_changed_columns(SHOPIFY_FILE, OUT_FILE_NAME, 'Variant SKU')
    print("Exiting...")