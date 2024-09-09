import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException


def read_data() -> dict:
    data = {}
    with open('model_data.json') as f:
        data = json.load(f)
    return data

def close_popup_if_exists(driver):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "newsletter-modal")))
        close_button = driver.find_element(By.CLASS_NAME, "close-reveal-modal")
        close_button.click()
        print("Popup closed.")
    except TimeoutException:
        print("Popup did not appear.")

def scrape_product_features(driver):
    features_dict = {}
    
    # Find all rows inside the product features section
    rows = driver.find_elements(By.CSS_SELECTOR, '.product-features .row')
    
    for row in rows:
        try:
            # Find the feature name in the <strong> tag
            feature_name_element = row.find_element(By.CSS_SELECTOR, '.small-4 strong')
            feature_value_element = row.find_element(By.CSS_SELECTOR, '.small-8')
        
            feature_name = feature_name_element.text.strip().replace(":", "") 
            feature_value = feature_value_element.text.strip()
            
            features_dict[feature_name] = feature_value
        except Exception as e:
            print(f"An error occurred while scraping feature: {e}")

    return features_dict

def write_product_to_json(product_data, filename='scraped_product_features.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
    else:
        data = {}
    
    data.update(product_data)
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def search_and_scrape(driver, search_query, handle_popup):
    driver.get("https://www.sportitude.com.au")

    try:
        search_box = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "unbxdInput"))
        )
        search_box.clear()
        search_box.send_keys(search_query)

        search_box.send_keys(Keys.RETURN)

        # Close the popup if this is the first time
        if handle_popup:
            close_popup_if_exists(driver)

        # Wait for the product item to appear and be clickable
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "product-item"))
        )
        product_item = driver.find_element(By.CLASS_NAME, "product-item")
        product_item.click()

        # Scrape the product features
        product_features = scrape_product_features(driver)

        # Write the features to a JSON file, with the search_query as the key
        write_product_to_json({search_query: product_features})

        print(f"Features for {search_query}: {product_features}")

        return True

    except TimeoutException:
        print(f"Timeout: Element not found for query: {search_query}.")
    except ElementNotInteractableException:
        print(f"Element not interactable for query: {search_query}.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return False


if __name__ == "__main__":
    data = read_data()
    driver = webdriver.Chrome()

    handle_popup = True

    for search_query in data.keys():
        success = search_and_scrape(driver, search_query, handle_popup)

        if success:
            handle_popup = False  # Close the popup only for the first product

        time.sleep(2)

    driver.quit()
