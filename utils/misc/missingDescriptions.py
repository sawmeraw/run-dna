import pandas as pd

def get_new_sku(sku: str):
    return ""


if __name__ == "__main__":
    file_path = './ready to upload/desc_all_processed_3.csv'

    df = pd.read_csv(file_path)

    missing_descriptions_df = df[pd.notna(df['Title']) & pd.isna(df['Body (HTML)'])]

    export_df = missing_descriptions_df[["Title", 'Variant SKU']]

    export_df.to_csv('./missing_descriptions.csv', index=False)

    print('Data exported')

        
    