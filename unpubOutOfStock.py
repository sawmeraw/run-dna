import pandas as pd


def read_stock_file(file_path: str)-> pd.DataFrame:
    df = pd.read_csv(file_path, low_memory=False)
    return df


def read_rex_file(file_path: str)-> pd.DataFrame:
    df = pd.read_csv(file_path, low_memory=False)
    return df


def filter_products_by_stock_and_publish(product_df: pd.DataFrame, stock_df: pd.DataFrame, output_file: str):
    product_df['SupplierSKU'] = product_df['SupplierSKU'].astype(str)
    stock_df['SupplierSKU'] = stock_df['SupplierSKU'].astype(str)


    product_df = product_df[product_df['Publish To:rundna-au.myshopify.com'] == True]
   
    merged_df = pd.merge(product_df, stock_df[['SupplierSKU', 'Stock']], on='SupplierSKU', how='left')
    # merged_df.to_csv('./test_mergeddf.csv', index=False)
   
    stock_summary = merged_df.groupby('SupplierSKU2')['Stock'].sum()
   
    out_of_stock_product_codes = stock_summary[stock_summary == 0].index.tolist()
   
    product_df['Publish To:rundna-au.myshopify.com'] = product_df['SupplierSKU2'].apply(
        lambda code: False if code in out_of_stock_product_codes else True
    )
   
    unpublished_product_df = product_df[product_df['Publish To:rundna-au.myshopify.com'] == False]
   
    unpublished_product_df.to_csv(output_file, index=False)
    print(f"Updated stock-based publish data saved to {output_file}")


if __name__ == "__main__":

    stock_file = read_stock_file('./utils/misc/stock_data/apparel_data.csv')
    rex_file = read_rex_file('./adidas_rex.csv')
   
    output_file = 'adidas_unpublished.csv'
   
    filter_products_by_stock_and_publish(product_df=rex_file, stock_df=stock_file, output_file=output_file)
   
    print('Exiting...')



