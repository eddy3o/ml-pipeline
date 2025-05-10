import os
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from pymongo import MongoClient 
import json
import time


MONGO_CONFIG = {
    "host": "localhost",
    "port": 27017,
    "db_name": "ScrapeV1",
    "collection_name": "Datos Investigacion"
}

def save_to_db(paragraphs):
    """Guarda los párrafos scrapeados en MongoDB."""
    try:
        client = MongoClient(MONGO_CONFIG["host"], MONGO_CONFIG["port"])
        db = client[MONGO_CONFIG["db_name"]]
        collection = db[MONGO_CONFIG["collection_name"]]

        for paragraph in paragraphs:
            
            paragraph = paragraph.encode('utf-8', 'ignore').decode('utf-8')

            
            content_json = {"text": paragraph}

            
            collection.insert_one(content_json)

        print("Datos guardados en MongoDB.")
    except Exception as e:
        print("Error guardando en MongoDB:", e)

def scrape_website(website):
    """Extrae contenido de la página y lo guarda en la base de datos."""
    print(f"Scraping {website}")

    chrome_driver_path = os.path.join(os.path.dirname(__file__), "chromedriver.exe")
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)

    try:
        driver.get(website)
        time.sleep(5)  

        
        post_containers = driver.find_elements(By.TAG_NAME, "p")
        posts = [post.text.replace("\n", " ").strip() for post in post_containers if post.text.strip()]

        print("Scraping completo.")

        
        save_to_db(posts)

        return posts
    except Exception as e:
        print(e)
        return []
    finally:
        driver.quit()