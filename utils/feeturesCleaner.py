import pandas as pd
import os

#E505578
#FEETURES ELITE LIGHT CUSHION NO-SHOW TAB SOCK (PUSH-THRU PINK) SZ S

#Works
def strip_color(description : str):
    startIndex = description.find('(')
    endIndex = description.find(')')
    color = description[startIndex + 1 : endIndex]
    return color.title().strip()


#Works
def process_feetures_sku(sku):
    return sku[:3]

#Works
def process_feetures_desc(desc: str, mansku: str) -> str:
    #Strip the color
    startIndex = desc.find('(')
    endIndex = desc.find(')')
    color = desc[startIndex + 1 : endIndex]

    first_part = desc[:startIndex]
    second_part = desc[endIndex+1:]
    combined = f"{first_part.strip()} ({mansku}) {color.strip()} {second_part.strip()}"
    return combined

#LIGHTFEET U EVOLUTION MINI SOCKS (SBU) SKY BLUE SZ S
def process_feetures_custom1(description :str) -> str:
    bracket_index = description.find('(')
    word_arr = description[:bracket_index].strip().split(' ')
    custom1 = ""
    for index, word in enumerate(word_arr):
        if index == len(word_arr) -1:
            custom1 += "Running Sock"
            return custom1
        custom1 += word.title() + " "
    return custom1

#LIGHTFEET U EVOLUTION MINI CREW SOCKS (PCO) FLURO PINK/CORAL SZ M
#LIGHTFEET SUPPORT INSOLE SZ S
#Works
def process_lightfeet_custom1(description : str) -> str:
    custom1 = ""

    if description.find('(') != -1:
        part = description[: description.find('(')].strip().title()
        arr = part.split(" ")
        for index, word in enumerate(arr):
            if word == "U":
                continue
            if index == len(arr) -1:
                custom1 += "Running Sock"
                return custom1
            custom1 += word + " "
        
        return custom1
    else:
        part = description[: description.find("SZ")].strip().title()
        arr = part.split(" ")
        return " ".join(arr)


#Works
def process_lightfeet_mansku(sku: str) -> str:
    if len(sku.split('-')) <=2:
        return sku
    else:
        arr = sku.split('-')
        new_sku = "-".join(arr[:len(arr)-1])
        return new_sku

#LIGHTFEET U EVOLUTION MINI CREW SOCKS (PCO) FLURO PINK/CORAL SZ M
#LIGHTFEET SUPPORT INSOLE SZ S
#Works
def process_lightfeet_desc(description:str, mansku : str) -> str : 
    if description.find("SOCK") != -1:
        startIndex = description.find('(')
        endIndex = description.find(')')
        
        new_desc = f"{description[:startIndex].strip()} ({mansku}) {description[endIndex+1:].strip()}"
    else:
        index = description.find("SZ")
        new_desc = f"{description[:index].strip()} ({mansku}) {description[index:]}"
    return new_desc

if __name__ == "__main__":
    brands = ["Lightfeet", "Feetures", "Salomon", "Shyu"]

    REX_FILE_PATH = './data/rex/feetures_rex_all.csv'
    rex_df = pd.read_csv(REX_FILE_PATH)
    rex_df['SupplierSKU2'] = rex_df['SupplierSKU2'].astype('object')
    rex_df['Custom1'] = rex_df['Custom1'].astype('object')
    rex_df['Colour'] = rex_df['Colour'].astype('object')


    #Feetures Logic
    for index, row in rex_df.iterrows():
        new_sku = process_feetures_sku(row['ManufacturerSKU'])
        new_desc = process_feetures_desc(row['ShortDescription'], row['ManufacturerSKU'])
        custom1 = process_feetures_custom1(row['ShortDescription'])
        color = strip_color(row['ShortDescription'])

        rex_df.at[index, 'SupplierSKU2'] = row['ManufacturerSKU']
        rex_df.at[index, 'ShortDescription'] = new_desc
        rex_df.at[index, 'Colour'] = color
        rex_df.at[index, 'Custom1'] = custom1
        rex_df.at[index, 'ManufacturerSKU'] = new_sku



    #Lightfeet logic
    # for index, row in rex_df.iterrows():
    #     rex_df.at[index, 'SupplierSKU2'] = row['ManufacturerSKU']
    #     color_name = strip_color(row['ShortDescription'])

    #     rex_df.at[index, "Colour"] = color_name

    #     custom1 = process_lightfeet_custom1(row['ShortDescription'])
    #     rex_df.at[index, 'Custom1'] = custom1

    #     new_desc = process_lightfeet_desc(row['ShortDescription'], row['ManufacturerSKU'])
    #     rex_df.at[index, 'ShortDescription'] = new_desc

    #     new_sku = process_lightfeet_mansku(row['ManufacturerSKU'])
    #     rex_df.at[index, 'ManufacturerSKU'] = new_sku



    rex_df.to_csv('./results/feetures_all_processed.csv', index=False)

    print("Done")