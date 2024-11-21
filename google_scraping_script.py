from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from datetime import datetime
import csv
import random
import requests

class GoogleWebDriver:
    def __init__(self, driver):
        """Initialize Web Driver"""
        self.driver = driver 

    def read_keywords(self):
        """Read keywords from the txt file and send them one by one to the 'navigate_googlepage' function"""
        keywords_file = '/Users/d.tanubudhi/Documents/google_scraping/keywords-for-AI-search.txt'
        
        try:
            with open(keywords_file, 'r') as file:
                keywords_list = file.read().splitlines()  

            for keyword in keywords_list:
                self.navigate_googlepage(keywords=keyword)
                time.sleep(3)  

                result = self.scraping_overview_ai()
                self.save_to_csv(result)
        except Exception as e:
            print(f"Error reading keywords or navigating: {e}")

    def navigate_googlepage(self, keywords: str) -> None:
        """Navigate to Google search page and enter keywords"""
        self.driver.get("https://www.google.com")
        time.sleep(2)
        
        try:
            cookie_element = self.driver.find_element(By.XPATH, '//*[@id="L2AGLb"]/div')
            self.driver.execute_script("arguments[0].click();", cookie_element)
        except:
            print("No such element")

        try:
            search_input = self.driver.find_element(By.NAME, 'q')
            search_input.clear()
            search_input.send_keys(keywords)
            search_input.send_keys(Keys.RETURN)
            time.sleep(2)
        except Exception as e:
            print(f"Error during navigation: {e}")

    def scraping_overview_ai(self) -> dict:
        """Attempt to scrape the AI OVERVIEW summary if present"""
        segments_info = {}
        segment_urls = []
        try:
            # Parse the page with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Look for the AI summary box class (might need updates as Google changes structure)
            ai_overview = soup.find("div", {"class": "f5cPye"})
            
            if ai_overview:
                summary_text = ai_overview.get_text(strip=True)
                segments_info['segment_title'] = self.driver.find_element(By.NAME, 'q').get_attribute('value')
                segments_info['summary'] = summary_text

                # Locate links within AI overview box
                links_segment = soup.find('ul', {'class': 'zVKf0d Cgh8Qc'})
                if links_segment:
                    for link in links_segment.find_all("a", {'class': 'KEVENd'}, href=True):
                        segment_urls.append(link['href'])
                
                segments_info['urls'] = segment_urls
            else:
                print("AI overview not found.")
        except Exception as e:
            print(f"Error during scraping AI overview: {e}")

        return segments_info
    
    def save_to_csv(self, scrape_data):
        """Save data to a CSV file"""
        if scrape_data:

            current_date = datetime.now().strftime('%Y-%m-%d')
            data_folder = '/Users/d.tanubudhi/Documents/google_scraping/Data'
            os.makedirs(data_folder, exist_ok=True)
            scrape_overview_path = os.path.join(data_folder, f'google-overviewai-{current_date}.csv')

            with open(scrape_overview_path, 'a', newline='', encoding='utf-8') as overview_file:
                overview_fieldnames = ['segment_title', 
                                       'summary', 
                                       'urls']
                file_writer = csv.DictWriter(overview_file, fieldnames=overview_fieldnames)
                
                # Only write header if file is new
                if overview_file.tell() == 0:
                    file_writer.writeheader()
                
                file_writer.writerow(scrape_data)
        else:
            print("No data to save.")

    # Download proxy list
    def download_proxy_list(self, 
        proxy_url: str = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=us&ssl=all&anonymity=all",
    ) -> None:
        """Downloading new proxy list from website to store into the file"""

        file_name = "/Users/d.tanubudhi/Documents/google_scraping/proxy_files/helper_proxy_urls.txt"
        r = requests.get(proxy_url)
        with open(file_name, "wb") as f:
            f.write(r.content)
        with open(file_name) as f:
            lines = f.read().splitlines()
        with open(file_name, "w") as f:
            for line in lines:
                print("http://" + line, file=f)

        return file_name

    # Getting random proxy
    def get_random_proxy(self, filename: str = "/Users/d.tanubudhi/Documents/Monthlt_Reports/proxy_files/helper_proxy_urls.txt") -> object:
        """Getting random proxy from list of proxies from text file and returning options for selenium"""

        options_proxy = {"proxy": {"http": None}}

        with open("/Users/d.tanubudhi/Documents/google_scraping/proxy_files/helper_proxy_urls.txt", "r") as file:
            lines = file.readlines()
            proxies = [line.strip() for line in lines if line.strip()]

        # Randomly pick one proxy
        random_proxy = random.choice(proxies)

        # Set the chosen proxy as the value for "http" key
        options_proxy["proxy"]["http"] = random_proxy

        # print(options_proxy)
        return options_proxy


if __name__ == "__main__":

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
    options.add_argument("--headless=new")
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    chrome = GoogleWebDriver(driver=driver)

    # Download new proxy list every time
    file_name = chrome.download_proxy_list()

    # Get random proxy
    options_proxy = chrome.get_random_proxy(file_name)
    
    try:
        chrome.read_keywords()
    finally:
        driver.quit()