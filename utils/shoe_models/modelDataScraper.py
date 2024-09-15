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
    with open('model_data.json') as f:
        return json.load(f)

def close_popup_if_exists(driver):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "newsletter-modal")))
        close_button = driver.find_element(By.CLASS_NAME, "close-reveal-modal")
        close_button.click()
        print("Popup closed.")
    except TimeoutException:
        print("Popup did not appear.")

def map_cushioning(cushioning_value: str) -> str:
    """Map Cushioning values based on custom logic."""
    mapping = {
        "Firm": "Low",
        "Balanced": "Medium",
        "Plush": "High",
        "Responsive": "Propulsive"
    }
    return mapping.get(cushioning_value, cushioning_value)  # Return mapped value or the original

def scrape_product_features(driver):
    features_dict = {}
    
    rows = driver.find_elements(By.CSS_SELECTOR, '.product-features .row')
    
    for row in rows:
        try:
            feature_name_element = row.find_element(By.CSS_SELECTOR, '.small-4 strong')
            feature_value_element = row.find_element(By.CSS_SELECTOR, '.small-8')
        
            feature_name = feature_name_element.text.strip().replace(":", "")
            feature_value = feature_value_element.text.strip()

            if feature_name == "Cushioning":
                feature_value = map_cushioning(feature_value)

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

def search_and_scrape(driver, search_query, gender, handle_popup):
    """Search and scrape the product for a specific gender."""
    query = f"{search_query} {gender}"
    driver.get("https://www.sportitude.com.au")

    try:
        search_box = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "unbxdInput"))
        )
        search_box.clear()
        search_box.send_keys(query)
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

        print(f"Features for {query}: {product_features}")
        return {gender: product_features}

    except TimeoutException:
        print(f"Timeout: Element not found for query: {query}.")
    except ElementNotInteractableException:
        print(f"Element not interactable for query: {query}.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return {}

if __name__ == "__main__":
    data = read_data()
    driver = webdriver.Chrome()

    handle_popup = True

    for search_query in data.keys():
        product_data = {}

        # Search and scrape for mens
        mens_data = search_and_scrape(driver, search_query, "mens", handle_popup)
        if mens_data:
            product_data.update(mens_data)

        # Search and scrape for womens
        womens_data = search_and_scrape(driver, search_query, "womens", handle_popup)
        if womens_data:
            product_data.update(womens_data)

        # Write to JSON file
        if product_data:
            write_product_to_json({search_query: product_data})

        handle_popup = False  # Close the popup only for the first product
        time.sleep(2) 

    driver.quit()
