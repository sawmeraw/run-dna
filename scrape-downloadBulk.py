import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from PIL import Image
from io import BytesIO
import pandas as pd
from imageDownloadBulk import clean_barcode, strip_title, sanitize_filename, get_product_code

def download_image(url, file_name):
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(IMAGE_FOLDER, file_name), 'wb') as f:
            f.write(response.content)
        print(f"Saved image: {file_name}")
    else:
        print(f"error response for file {file_name}")


def clean_img_urls(urls : list[str]):

    img_set = []
    for url in urls:
        if url not in img_set:
            img_set.append(url)
    
    new_image_list= []
    for url in img_set:
        if "__S" in url:
            newUrl = url.replace("__S", "__L")
        else:
            newUrl = url.replace(".jpg", "__L.jpg")
        new_image_list.append(newUrl)

    return new_image_list


def scrape_images_after_search(search_query,file_name):
    driver = webdriver.Chrome()
    driver.get("https://www.sportitude.com.au")

    search_box = driver.find_element(By.ID, "unbxdInput")
    search_box.send_keys(search_query)

    search_box.send_keys(Keys.RETURN)

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "product-item")))
        product_item = driver.find_element(By.CLASS_NAME, "product-item")
        product_item.click()
    except TimeoutException:
        print("Element with class name 'product_item' not found within the time frame.")
        driver.quit()
        return

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "photo-grid-wrapper")))

    photo_grid = driver.find_elements(By.CLASS_NAME, "photo-grid")
    photo_grid_more = driver.find_elements(By.CLASS_NAME, "photo-grid-more")

    photo_grid.extend(photo_grid_more)


    img_url_list = []
    for grid in photo_grid:
        images = grid.find_elements(By.TAG_NAME, "img")
        for img in images:
            img_url = img.get_attribute("src")
            if img_url:
                img_url_list.append(img_url)

    image_urls = clean_img_urls(img_url_list)

    for i, url in enumerate(image_urls, start=1):
        curr_file_name = f"{file_name}-{i}.jpg"
        download_image(url, curr_file_name)


if __name__ == "__main__":

    file_name = 'mizuno4_export'

    REX_FILE_PATH = os.path.join(os.getcwd(), 'data/rex/mizuno_rex.csv')
    SHOPIFY_FILE_PATH = os.path.join(os.getcwd(), f'data/{file_name}.csv')

    rex_df = pd.read_csv(REX_FILE_PATH)
    shopify_df = pd.read_csv(SHOPIFY_FILE_PATH)

    IMAGE_FOLDER = os.path.join(os.getcwd(), "images")
    DRIVER_PATH = os.path.join(os.getcwd(), 'driver/chromedriver')

    products_dict = {}
    currTitle = ""

    for index, row in shopify_df.iterrows():
        title = row['Title']
        color = row['Option2 Value']
        barcode = clean_barcode(row['Variant SKU'])

        if pd.notna(title):
            currTitle = title

        if pd.notna(color) and pd.notna(barcode):
            stripped_title = sanitize_filename(strip_title(currTitle))
            stripped_color = sanitize_filename(color)
            
            key = f"{stripped_title}-{stripped_color}"
            
            products_dict[key] = barcode


    print("Products Dictionary:")
    for key, barcode in products_dict.items():
        print(f"Key: {key}, Barcode: {barcode}")

    for key, barcode in products_dict.items():
        found = False
        for _, rex_row in rex_df.iterrows():
            barcode = str(barcode)
            supplier_sku = str(rex_row['SupplierSKU'])
            if barcode in supplier_sku:
                found = True
                description = rex_row['ShortDescription']
                product_code = get_product_code(description)
                scrape_images_after_search(product_code, os.path.join(IMAGE_FOLDER, key))

    print("Done")


