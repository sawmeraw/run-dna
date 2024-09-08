import pandas as pd
import re

def filter_products_by_stock(product_file: str, stock_file: str, output_file: str):
    product_df = pd.read_csv(product_file)

    stock_df = pd.read_csv(stock_file)

    product_df['ProductCode'] = product_df['SupplierSKU2']

    product_df['SupplierSKU'] = product_df['SupplierSKU'].astype(str)
    stock_df['SupplierSKU'] = stock_df['SupplierSKU'].astype(str)

    merged_df = pd.merge(product_df, stock_df[['SupplierSKU', 'Stock']], on='SupplierSKU', how='left')

    stock_summary = merged_df.groupby('ProductCode')['Stock'].sum()

    in_stock_product_codes = stock_summary[stock_summary > 0].index.tolist()

    filtered_products_df = product_df[product_df['ProductCode'].isin(in_stock_product_codes)]

    filtered_products_df.to_csv(output_file, index=False)

    print(f"Filtered products with stock saved to {output_file}")

if __name__ == "__main__":
    # Paths to your files
    product_file = './results/nike_app_processed.csv'
    stock_file = './stock_data/apparel_data.csv'   
    output_file = '.nike_app_processed_stock_checked.csv'

    # Call the function to filter products by stock
    filter_products_by_stock(product_file, stock_file, output_file)