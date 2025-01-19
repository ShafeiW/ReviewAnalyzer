from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pickle
import os
import time

def save_cookies(driver, cookies_file):
    """Save cookies to a file."""
    pickle.dump(driver.get_cookies(), open(cookies_file, "wb"))

def load_cookies(driver, cookies_file):
    """Load cookies from a file if it exists."""
    if os.path.exists(cookies_file):
        cookies = pickle.load(open(cookies_file, "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        print("Cookies loaded successfully.")
    else:
        print("Cookies file not found.")

def login_to_amazon(driver):
    driver.get("https://www.amazon.ca/ap/signin")
    try:
        print("Navigating to login page...")
        with open("login_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        driver.save_screenshot("login_page.png")
        
        email_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "ap_email"))
        )
        email_field.send_keys("shafeitest9@example.com")
        print("Email entered successfully.")

        continue_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "continue"))
        )
        continue_button.click()
        print("Clicked 'Continue' button.")

        password_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "ap_password"))
        )
        password_field.send_keys("PasswordTest360")
        print("Password entered successfully.")

        sign_in_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "signInSubmit"))
        )
        sign_in_button.click()
        print("Clicked 'Sign-In' button.")

        # Save the page source for debugging
        driver.save_screenshot("post_login.png")
        with open("post_login_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Login completed.")

    except Exception as e:
        print(f"Error during login: {e}")
        driver.save_screenshot("login_error.png")
        raise


def scrape_amazon_reviews(product_url, num_pages=1, cookies_file="cookies.pkl"):
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    reviews = []

    try:
        if os.path.exists(cookies_file):
            # Load cookies if available
            driver.get("https://www.amazon.ca")
            load_cookies(driver, cookies_file)
            driver.refresh()
            print("Cookies loaded and refreshed.")
        else:
            # Perform login and save cookies
            login_to_amazon(driver)
            save_cookies(driver, cookies_file)
            print("Cookies saved successfully.")

        for page in range(1, num_pages + 1):
            url = f"{product_url}&pageNumber={page}"
            driver.get(url)
            time.sleep(5)

            # Save review page source for debugging
            with open(f"review_page_source_{page}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print(f"Saved review page source for page {page} to 'review_page_source_{page}.html'.")

            # Extract reviews
            review_elements = driver.find_elements(By.CSS_SELECTOR, "span[data-hook='review-body']")
            if not review_elements:
                print(f"No reviews found on page {page}. Exiting.")
                break

            for element in review_elements:
                reviews.append(element.text.strip())

            print(f"Scraped {len(review_elements)} reviews from page {page}.")
            time.sleep(3)

    except Exception as e:
        print(f"Error during scraping: {e}")
        driver.save_screenshot("scraping_error.png")
    
    finally:
        driver.quit()

    return reviews

if __name__ == "__main__":
    product_url = "https://www.amazon.ca/product-reviews/B07CRG94G3/ref=cm_cr_arp_d_viewopt_sr?ie=UTF8&filterByStar=all_stars&reviewerType=all_reviews&pageNumber=1"
    num_pages = 5

    reviews = scrape_amazon_reviews(product_url, num_pages=num_pages)

    if reviews:
        print(f"Scraped {len(reviews)} reviews.")
    else:
        print("No reviews found.")
