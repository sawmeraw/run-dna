import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
import pandas as pd
from imageDownloadBulk import clean_barcode, strip_title, sanitize_filename, get_product_code
import time


def download_image(url, file_name):
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(IMAGE_FOLDER, file_name), 'wb') as f:
            f.write(response.content)
        print(f"Saved image: {file_name}")
    else:
        print(f"Error response for file {file_name}")


def clean_img_urls(urls: list[str]) -> list[str]:
    img_set = []
    for url in urls:
        if url not in img_set:
            img_set.append(url)

    new_image_list = []
    for url in img_set:
        if "__S" in url:
            newUrl = url.replace("__S", "__L")
        else:
            newUrl = url.replace(".jpg", "__L.jpg")
        new_image_list.append(newUrl)

    return new_image_list


def close_popup_if_exists(driver):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "newsletter-modal")))
        close_button = driver.find_element(By.CLASS_NAME, "close-reveal-modal")
        close_button.click()
        print("Popup closed.")
    except TimeoutException:
        print("Popup did not appear.")


def scrape_images_after_search(driver, search_query, file_name, handle_popup):
    driver.get("https://www.sportitude.com.au")

    try:
        # Wait for the search box to be clickable and input search query
        search_box = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "unbxdInput")))
        search_box.clear()
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        
        # Wait for product item and ensure it's clickable
        product_item = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "product-item")))

        # Add a small wait to ensure the element is fully loaded
        time.sleep(2)
        # Click the product item
        product_item.click()

        # Wait for the photo grid to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "photo-grid-wrapper")))

        if handle_popup:
            close_popup_if_exists(driver)

        time.sleep(2)
        # Scrape images
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

        # Clean image URLs
        image_urls = clean_img_urls(img_url_list)

        # Download images
        for i, url in enumerate(image_urls, start=1):
            curr_file_name = f"{file_name}-{i}.jpg"
            download_image(url, curr_file_name)

    except TimeoutException:
        print(f"Element with class name 'product-item' not found for query: {search_query}.")
    except ElementNotInteractableException:
        print(f"Element not interactable for query: {search_query}.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return


if __name__ == "__main__":
    # Initialize variables
    file_name = 'vivo_export'

    REX_FILE_PATH = os.path.join(os.getcwd(), 'vivo_rex.csv')
    SHOPIFY_FILE_PATH = os.path.join(os.getcwd(), f'{file_name}.csv')

    rex_df = pd.read_csv(REX_FILE_PATH)
    shopify_df = pd.read_csv(SHOPIFY_FILE_PATH)

    IMAGE_FOLDER = os.path.join(os.getcwd(), "images")

    # Set up WebDriver
    driver = webdriver.Chrome()

    products_dict = {}
    currTitle = ""
    handle_popup = True  # Flag to manage popup closure

    # Build products dictionary
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

    # Perform scraping for each product in products_dict
    for key, barcode in products_dict.items():
        found = False
        for _, rex_row in rex_df.iterrows():
            barcode = str(barcode)
            supplier_sku = str(rex_row['SupplierSKU'])
            if barcode in supplier_sku:
                found = True
                description = rex_row['ShortDescription']
                product_code = get_product_code(description=description)

                # Scrape images using the product code
                scrape_images_after_search(driver, product_code, os.path.join(IMAGE_FOLDER, key), handle_popup)

                # After the first popup is handled, set the flag to False
                handle_popup = False

                time.sleep(2)

    driver.quit()
    print("Done")
