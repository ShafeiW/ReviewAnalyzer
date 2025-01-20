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
import csv

def save_cookies(driver, cookies_file):
    """Save cookies to a file."""
    try:
        with open(cookies_file, "wb") as file:
            pickle.dump(driver.get_cookies(), file)
        print("Cookies saved successfully.")
    except Exception as e:
        print(f"Error saving cookies: {e}")


def load_cookies(driver, cookies_file, target_domain):
    """Load cookies for the target domain."""
    try:
        if os.path.exists(cookies_file):
            with open(cookies_file, "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    if "domain" in cookie:
                        cookie["domain"] = target_domain
                    driver.add_cookie(cookie)
            print("Cookies loaded successfully.")
        else:
            print("Cookies file not found.")
    except Exception as e:
        print(f"Error loading cookies: {e}")



def login_to_amazon(driver):
    """Automate the login process with explicit waits for each step."""
    driver.get("https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0")
    try:
        # Wait for email input field
        email_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "ap_email"))
        )
        email_field.send_keys("shafeitest9@gmail.com")
        print("Email entered successfully.")

        # Wait for and click "Continue" button
        continue_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "continue"))
        )
        continue_button.click()
        print("Clicked 'Continue' button.")

        # Save page source for debugging
        with open("post_email_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        # Wait for password input field
        password_field = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "ap_password"))
        )
        password_field.send_keys("PasswordTest360")
        print("Password entered successfully.")

        # Wait for and click "Sign-In" button
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "signInSubmit"))
        )
        sign_in_button.click()
        print("Clicked 'Sign-In' button.")

        # Complete Captcha manually
        time.sleep(10)

        # Save post-login page source for verification
        with open("post_login_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        time.sleep(5)
        print("Login successful!")

    except Exception as e:
        print(f"Error during login: {e}")
        with open("login_error_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved login error page source.")



def scrape_amazon_reviews(product_url, num_pages=5, cookies_file="cookies.pkl"):
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    reviews = []

    try:
        # Load cookies or log in
        if os.path.exists(cookies_file):
            driver.get("https://www.amazon.com")
            load_cookies(driver, cookies_file, ".amazon.com")
            driver.refresh()
            time.sleep(5)
            print("Cookies loaded successfully.")
            if "ap/signin" in driver.current_url:
                print("Session invalid. Reattempting login.")
                login_to_amazon(driver)
                save_cookies(driver, cookies_file)
        else:
            login_to_amazon(driver)
            save_cookies(driver, cookies_file)
            print("Cookies saved successfully.")

        for page in range(1, num_pages + 1):
            # Construct the URL for each page
            if page == 1:
                url = product_url
            else:
                url = product_url.replace(
                    "ref=cm_cr_arp_d_viewopt_srt",
                    f"ref=cm_cr_arp_d_paging_btm_next_{page}"
                ).replace("pageNumber=1", f"pageNumber={page}")
            
            print(f"Navigating to page {page}: {url}")
            driver.get(url)
            time.sleep(5)

            # Scroll to ensure all content loads
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            # Extract reviews
            review_elements = driver.find_elements(By.CSS_SELECTOR, "span[data-hook='review-body']")
            if not review_elements:
                print(f"No reviews found on page {page}.")
                break

            for element in review_elements:
                reviews.append(element.text.strip())

            print(f"Scraped {len(review_elements)} reviews from page {page}.")

            # Save page source for debugging
            with open(f"review_page_source_{page}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)

    except Exception as e:
        print(f"Error during scraping: {e}")
        driver.save_screenshot("error_screenshot.png")
        with open("error_debug_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
    finally:
        driver.quit()

    return reviews




if __name__ == "__main__":
    product_url = "https://www.amazon.com/product-reviews/B0B16HXVVQ/ref=cm_cr_arp_d_viewopt_srt?ie=UTF8&filterByStar=all_stars&reviewerType=all_reviews&pageNumber=1"
    num_pages = 5

    reviews = scrape_amazon_reviews(product_url, num_pages=num_pages)

    if reviews:
        print(f"Scraped {len(reviews)} reviews.")
        # Save reviews to a CSV file
        with open("amazon_reviews.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Review"])  # Add header
            writer.writerows([[review] for review in reviews])
        print("Reviews saved to 'amazon_reviews.csv'.")
    else:
        print("No reviews found.")

