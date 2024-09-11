import pandas as pd
import json
import os

def read_data():
    data = {}
    with open('./scraped_product_features.json') as f:
        data = json.load(f)
    return data

def load_model_data(df: pd.DataFrame, model_data: dict):
    for index, row in df.iterrows():
        currTitle = row['Title']
        if pd.notna(currTitle):
            model = get_model_data(currTitle, model_data)
            
            if model:
                # Split title, clean each word, and check for gender
                title_words = [word.lower().strip() for word in currTitle.split()]
                gender_data = None

                if "mens" in title_words:
                    gender_data = model.get('mens', {})
                    print(f"Matched mens data for title: {currTitle}")
                elif "womens" in title_words:
                    gender_data = model.get('womens', {})
                    print(f"Matched womens data for title: {currTitle}")
                elif "unisex" in title_words:
                    gender_data = model.get('mens', {})
                    print(f"Matched unisex data, using mens data for title: {currTitle}")
                else:
                    print(f"Warning: Could not determine gender for title: {currTitle}. Skipping.")
                    continue  # Skip if no gender is detected

                # Debugging: Ensure correct data is being applied
                print(f"Gender data being applied for {currTitle}: {gender_data}")

                # Check and populate fields, make sure the columns exist or create them
                if 'Cushioning' in gender_data:
                    df.at[index, 'Cushioning (product.metafields.productspecs.cushioning)'] = gender_data['Cushioning']
                if 'Drop' in gender_data:
                    df.at[index, 'Drop (product.metafields.productspecs.drop)'] = gender_data['Drop']
                if 'Heel Height' in gender_data:
                    df.at[index, 'Heel Stack (product.metafields.productspecs.heel_stack)'] = gender_data['Heel Height']
                if 'Support' in gender_data:
                    df.at[index, 'Support (product.metafields.productspecs.support)'] = gender_data['Support']
                if 'Surface' in gender_data:
                    df.at[index, 'Surface (product.metafields.productspecs.surface)'] = gender_data['Surface']
                if 'Weight' in gender_data:
                    df.at[index, 'Weight (product.metafields.productspecs.weight)'] = gender_data['Weight']
                    print(f"Weight applied for {currTitle}: {gender_data['Weight']}")
            else:
                print(f"No matching model found for title: {currTitle}")
    
    # Save the updated DataFrame to a CSV file
    df.to_csv('./model_data_loaded.csv', index=False)
    print('File saved to the current script directory')


def get_model_data(title: str, data: dict):
    """Matches the title with a model in the data."""
    print(f"Searching for model for title: {title}")
    for model in data.keys():
        model_arr = model.split(' ')
        found = True

        for word in model_arr:
            if word.strip().lower() not in title.strip().lower():
                found = False
                break
        
        if found:
            print(f"Match found: {model}")
            return data[model]  # Return the model dictionary (contains 'mens' and 'womens')
    
    print("No match found for title:", title)
    return None


if __name__ == "__main__":
    model_data = read_data()

    SHOPIFY_FILE_PATH = './attributes_to_update.csv'

    df = pd.read_csv(SHOPIFY_FILE_PATH, low_memory=False)

    load_model_data(df, model_data=model_data)

    print('Done')
