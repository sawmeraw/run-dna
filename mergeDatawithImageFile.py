import pandas as pd

def read_file(file_path: str)-> pd.DataFrame:
    df = pd.read_csv(file_path, low_memory=False)
    return df

def strip_name(name: str)-> str:
    return name.split('- ')[0].strip()

def detect_gender_from_title(title: str) -> str:
    """Detect the gender based on substrings in the title."""
    title_lower = title.lower()
    if "mens" in title_lower:
        return "mens"
    elif "womens" in title_lower:
        return "womens"
    elif "unisex" in title_lower:
        return "unisex"
    else:
        return "unknown"
    

def update_images_df_with_description(images_df: pd.DataFrame, data_df: pd.DataFrame) -> pd.DataFrame:
    # Iterate through each row in images_df
    for img_index, img_row in images_df.iterrows():
        img_title = img_row['Title']
        img_cleaned_title = strip_name(img_title)  # Cleaned title for matching
        detected_gender = detect_gender_from_title(img_title)  # Detect gender from the title

        # Look for matching title and gender in data_df
        for data_index, data_row in data_df.iterrows():
            data_title = data_row['Title'].strip()
            data_gender = data_row['Gender'].strip().lower()

            # Match based on cleaned title and gender
            if img_cleaned_title.lower() == data_title.lower() and data_gender == detected_gender:
                # Update the 'Description' column in images_df with the matched description from data_df
                description = data_row.get('Description', '')
                cushioning = data_row.get('Cushioning', '')
                drop = data_row.get('Drop', '')
                heel_stack = data_row.get('Heel Stack', '')
                support = data_row.get('Support', '')
                best_for = data_row.get('Best For', '')
                weight = data_row.get('Weight', '')
                no_of_pins = data_row.get('Number of Pins', '')

                if pd.notna(description) and description != 'nan':
                    images_df.at[img_index, 'Description'] = description
                if pd.notna(description) and description != 'nan':
                    images_df.at[img_index, 'Description'] = description
                if pd.notna(cushioning) and cushioning != 'nan':
                    images_df.at[img_index, 'Cushioning'] = cushioning
                if pd.notna(drop) and drop != 'nan':
                    images_df.at[img_index, 'Drop'] = drop
                if pd.notna(heel_stack) and heel_stack != 'nan':
                    images_df.at[img_index, 'Heel Stack'] = heel_stack
                if pd.notna(support) and support != 'nan':
                    images_df.at[img_index, 'Support'] = support
                if pd.notna(best_for) and best_for != 'nan':
                    images_df.at[img_index, 'Best For'] = best_for
                if pd.notna(weight) and weight != 'nan':
                    images_df.at[img_index, 'Weight'] = weight
                if pd.notna(no_of_pins) and no_of_pins != 'nan':
                    images_df.at[img_index, 'Number of Pins'] = no_of_pins
                
                break  # Stop searching once a match is found for this image
    
    # Create a DataFrame with the result rows
    
    images_df.to_csv('./merged_files.csv', index=False)
    


if __name__ ==  "__main__":
    data_df = read_file('data.csv')
    images_df = read_file('updating_images.csv')

    update_images_df_with_description(data_df=data_df, images_df=images_df)
    print('Done')
