from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json
import time

def scrape_newegg_reviews(product_url, max_pages=5):
    reviews = []
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    driver.get(product_url)

    for page in range(1, max_pages + 1):
        time.sleep(3)  # Wait for dynamic content to load
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        review_blocks = soup.find_all('div', class_='item-review')

        for block in review_blocks:
            try:
                title = block.find('strong').text.strip()
                text = block.find('p', class_='comments').text.strip()
                rating = int(block.find('i', class_='rating').get('class')[1].split('-')[-1])

                reviews.append({
                    'title': title,
                    'text': text,
                    'rating': rating,
                })
            except Exception as e:
                print(f"Error parsing review: {e}")

        # Check for next page
        try:
            next_button = driver.find_element(By.CLASS_NAME, 'pagination-next')
            next_button.click()
        except Exception as e:
            print(f"No more pages: {e}")
            break

    driver.quit()
    return reviews

def save_reviews_to_json(reviews, output_file):
    with open(output_file, 'w') as f:
        json.dump(reviews, f, indent=4)
