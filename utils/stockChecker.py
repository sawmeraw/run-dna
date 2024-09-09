import pandas as pd



if __name__ == "__main__":

    product_df = pd.read_csv("./results/nike_app_processed.csv", low_memory=False)
    stock_df = pd.read_csv('./stock_data/apparel_data.csv', low_memory=False)

    # Filter the manufacturer SKUs where stock is greater than 0
    in_stock_skus = stock_df['ManufacturerSKU'].unique()

    # Filter the product DataFrame to include only products with in-stock Manufacturer SKUs
    filtered_products_df = product_df[product_df['ManufacturerSKU'].isin(in_stock_skus)].copy()

    filtered_products_df.to_csv("nike_app_processed_stock_checked.csv", index=False)

    print(f"Products with stock saved to asics_kids_all_processed_v2_stock_checked,csv")