import pandas as pd
import os
import json

def read_data()-> dict:
    data = {}
    with open('scraped_product_features.json') as f:
        data = json.load(f)
    return data

def load_model_data(df : pd.DataFrame, model_data : dict):

    for index, row in df.iterrows():
        currTitle = row['Title']
        if pd.notna(currTitle):
            model = get_model_data(currTitle, model_data)
            
            if model:
                
                if 'Cushioning' in model:
                    df.at[index, 'Cushioning (product.metafields.productspecs.cushioning)'] = model['Cushioning']
                if 'Drop' in model:
                    df.at[index, 'Drop (product.metafields.productspecs.drop)'] = model['Drop']
                if 'Heel Height' in model:
                    df.at[index, 'Heel Stack (product.metafields.productspecs.heel_stack)'] = model['Heel Height']
                if 'Support' in model:
                    df.at[index, 'Support (product.metafields.productspecs.support)'] = model['Support']
                if 'Surface' in model:
                    df.at[index, 'Surface (product.metafields.productspecs.surface)'] = model['Surface']
                if 'Weight' in model:
                    df.at[index, 'Weight (product.metafields.productspecs.weight)'] = model['Weight']
            

    df.to_csv('./model_data_loaded.csv')
    print('File saved to the current script directory')   




def get_model_data(title : str, data: dict):

    print(title)
    for model in data.keys():
        model_arr = model.split(' ')
        found = True

        for word in model_arr:
            if word.strip().lower() not in title.strip().lower():
                found = False
                break
        
        if found:
            return data[model]
        
    return None


#Cushioning (product.metafields.productspecs.cushioning)
#Drop (product.metafields.productspecs.drop)	
#Heel Stack (product.metafields.productspecs.heel_stack)
#Support (product.metafields.productspecs.support)
#Surface (product.metafields.productspecs.surface)

if __name__ == "__main__":
    model_data = read_data()

    SHOPIFY_FILE_PATH = './products_export_1.csv'

    df = pd.read_csv(SHOPIFY_FILE_PATH, low_memory=False)

    load_model_data(df, model_data=model_data)


    print('Done')
