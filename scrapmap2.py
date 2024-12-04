from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
import csv


def scrape_google_maps_data(search_query):
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    try:
        # Navigate to Google Maps
        driver.get(f'https://www.google.com/maps/search/{search_query}')
        results_container_selector = '.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd'
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, results_container_selector)))

        business_urls = set()
        scroll_and_collect(driver, business_urls, results_container_selector)

        # Scrape details for each business
        data = []
        for business_url in business_urls:
            business_data = scrape_business_data(driver, business_url)
            if business_data:
                data.append(business_data)

        return data

    except Exception as e:
        print(f"Could not collect data for {search_query}: {e}")
        return []
    finally:
        driver.quit()


def scroll_and_collect(driver, business_urls, results_container_selector):
    try:
        results_container = driver.find_element(By.CSS_SELECTOR, results_container_selector)
        while True:
            new_urls = results_container.find_elements(By.CSS_SELECTOR, 'a[href^="https://www.google.com/maps/place"]')
            for anchor in new_urls:
                business_urls.add(anchor.get_attribute('href'))

            driver.execute_script("return arguments[0].scrollIntoView();", new_urls[-1])
            time.sleep(2)

            # Check if the end of the list is reached
            page_text = driver.find_element(By.TAG_NAME, 'body').text
            if "You've reached the end of the list." in page_text:
                break
    except Exception as e:
        print(f"An error occurred during scrolling: {e}")


def scrape_business_data(driver, business_url):
    try:
        print(f"Fetching data from: {business_url}")
        driver.get(business_url)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.DUwDvf.lfPIob')))

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract data
        name = soup.find('h1', class_='DUwDvf lfPIob').get_text(strip=True) if soup.find('h1', class_='DUwDvf lfPIob') else 'N/A'
        reviews_element = soup.find('span', attrs={'aria-label': re.compile(r'reviews')})
        number_of_reviews = reviews_element.get_text(strip=True).split('(')[1].replace(')', '').replace(',', '') if reviews_element else 'N/A'

        ratings_element = soup.find('span', class_='ceNzKf', role='img')
        ratings = ratings_element.get('aria-label').split(' ')[0] if ratings_element else 'N/A'

        address = soup.find('div', class_='Io6YTe fontBodyMedium kR99db fdkmkc').get_text(strip=True) if soup.find('div', class_='Io6YTe fontBodyMedium kR99db fdkmkc') else 'N/A'

        phone_divs = soup.find_all('div', class_='Io6YTe fontBodyMedium kR99db fdkmkc')
        phone = 'N/A'
        phone_regex = r'(\+?\d{1,2}\s*[-.\s]?)?(\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}'
        
        for div in phone_divs:
            text = div.get_text(strip=True)
            if re.match(phone_regex, text):
                phone = text
                break
            
        website_elements = soup.find_all('div', class_='rogA2c ITvuef')
        website = next((el.get_text(strip=True) for div in website_elements for el in div.find_all('div', class_='Io6YTe') if '.' in el.get_text()), 'N/A')

        return {'name': name, 'ratings': ratings, 'number_of_reviews': number_of_reviews, 'phone': phone, 'website': website, 'address': address, 'link': business_url}

    except Exception as e:
        print(f"Failed to scrape {business_url}: {e}")
        return None


def save_to_csv(data, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'ratings', 'number_of_reviews', 'phone', 'website', 'address', 'link'])
        writer.writeheader()
        writer.writerows(data)
    print(f"Data saved to {filename}")


def main():
    search_queries = [
        "IT companies in The Loop Chicago",
        "IT companies in River North Chicago",
        "IT companies in Fulton Market Chicago",
        "IT companies in West Loop Chicago",
        "IT companies in Lincoln Park Chicago",
        "Tech startups in Wicker Park Chicago",
        "Tech companies in South Loop Chicago",
        "IT companies in Logan Square Chicago",
        "Tech startups in Bridgeport Chicago",
        "IT companies in Edgewater Chicago",
        "Tech companies in Hyde Park Chicago",
        "Tech startups in Pilsen Chicago"
    ]

    unique_companies = set() 
    combined_data = []  # To store all unique results

    for search_query in search_queries:
        try:
            print(f"Starting search for: {search_query}")
            data = scrape_google_maps_data(search_query)
            for company in data:
                if company['name'] not in unique_companies:
                    unique_companies.add(company['name'])
                    combined_data.append(company)
            print(f"Search completed for: {search_query}")
        except Exception as e:
            print(f"Error occurred during the search for {search_query}: {e}")

    # Save combined unique data to a single CSV file
    save_to_csv(combined_data, "IT_Companies_Chicago.csv")
    print("All unique data saved to 'Unique_IT_Companies_Chicago.csv'")
# def main():
#     locations = [
#         "Hackensack, NJ",
#         "Fort Lee, NJ",
#         "Teaneck, NJ",
#         "Ridgefield Park, NJ",
#         "Englewood, NJ"
#         # "Cliffside Park, NJ",
#         # "Leonia, NJ",
#         # "Fairview, NJ"
#     ]

#     search_queries = [f"food market in {location} US" for location in locations]
#     unique_companies = set()
#     combined_data = []

#     for search_query in search_queries:
#         print(f"Starting search for: {search_query}")
#         try:
#             data = scrape_google_maps_data(search_query)
#             for company in data:
#                 if company['name'] not in unique_companies:
#                     unique_companies.add(company['name'])
#                     combined_data.append(company)
#             print(f"Search completed for: {search_query}")
#         except Exception as e:
#             print(f"Error occurred during the search for {search_query}: {e}")

#     save_to_csv(combined_data, "Food_Markets_East_Bergen.csv")
#     print("All unique data saved to 'Food_Markets_East_Bergen.csv'")



if __name__ == "__main__":
    main()
