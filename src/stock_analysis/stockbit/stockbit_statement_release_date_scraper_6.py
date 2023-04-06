import json
import os
import re
from datetime import datetime
from time import sleep
from typing import Optional

import redis

import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class StockbitScraper:
    def __init__(self):
        # Define chrome options
        chrome_options = webdriver.ChromeOptions()

        # open Browser in maximized mode
        chrome_options.add_argument("start-maximized")
        # disabling infobars
        chrome_options.add_argument("disable-infobars")
        # overcome limited resource problems
        chrome_options.add_argument("--disable-dev-shm-usage")
        # disabling extensions
        chrome_options.add_argument("--disable-extensions")
        # disabling gpu, applicable to windows os only
        chrome_options.add_argument("--disable-gpu")
        # bypass OS security model
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), chrome_options=chrome_options
        )

        # Initialize Redis
        self.redis = redis.Redis(
            host=os.environ["REDIS_HOST"],
            port=os.environ["REDIS_PORT"],
            password=os.environ["REDIS_PASSWORD"]
        )

    def login(self, username, password):
        self.driver.get("https://stockbit.com/#/login")
        sleep(3)
        input_username = self.driver.find_element(By.XPATH, '//*[@id="username"]')
        input_username.send_keys(username)
        input_password = self.driver.find_element(By.XPATH, '//*[@id="password"]')
        input_password.send_keys(password)

        # Click login button
        self.driver.find_element(By.XPATH, '//*[@id="email-login-button"]').click()
        sleep(3)

    def parse_date_title(self, text):
        try:
            regex = r'^.*\n(\d{1,2}\s\w{3}\s\d{2})[^[\n]*\n([^\n]*(?:(?!\n\d+\slikes\s\d+|\n$).)*)'
            match = re.search(regex, text)
            date_str = match.group(1)
            date_format = '%d %b %y'
            date_obj = datetime.strptime(date_str, date_format)
            date_str = date_obj.strftime('%Y%m%d')
            title_str = match.group(2)
        except:
            date_str = None
            title_str = None
        return date_str, title_str

    def get_statement_release_dates(
        self,
        stock_filter: Optional[list] = None,
        year_filter: Optional[list] = None,
        period_filter: Optional[list] = None,
    ):

        # Filter
        if stock_filter:
            if isinstance(stock_filter, str):
                stock_filter = list(stock_filter.split(","))

        # Get stocks
        stocks = stock_filter
        for stock in stocks:
            try:
                # Define url
                url = f"https://stockbit.com/#/symbol/{stock}"

                try:
                    # Go to url
                    self.driver.get(url)
                    sleep(4)
                except:
                    print(f"Cannot access fundamental data for stock: {stock}")
                    continue

                reports_btn = self.driver.find_element(
                    By.XPATH,
                    '//*[@id="main-container"]/div[4]/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/button[3]',
                )
                self.driver.execute_script("arguments[0].click();", reports_btn)

                search_btn = self.driver.find_element(
                    By.XPATH,
                    '//*[@id="main-container"]/div[4]/div[1]/div[2]/div[2]/div[1]/div[1]/div[4]/div/div/p',
                )
                self.driver.execute_script("arguments[0].click();", search_btn)
                sleep(0.5)

                search_input = self.driver.find_element(By.XPATH, '//*[@id="main-container"]/div[4]/div[1]/div[2]/div[2]/div[1]/div[2]/div/form/span/input')
                search_input.send_keys("Laporan Keuangan")
                search_input.submit()
                sleep(1)

                # Get scroll height
                last_height = self.driver.execute_script("return document.body.scrollHeight")

                while True:
                    # Scroll down to bottom
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                    # Wait to load page
                    sleep(3)

                    # Calculate new scroll height and compare with last scroll height
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        # If heights are the same it will exit the function
                        break
                    last_height = new_height

                elements = self.driver.find_elements(
                    By.XPATH,
                    '//*[@id="main-container"]/div[4]/div[1]/div[2]/div[2]/div',
                )
                release_date_list = []
                for element in elements:
                    date, title = self.parse_date_title(element.text)
                    if date and title:
                        release_date_dict = {
                            "date": date,
                            "title": title,
                        }
                        release_date_list.append(release_date_dict)
                    else:
                        continue
                
                self.redis.set(f'{stock}', json.dumps(release_date_list))
                print(f"{stock}: Succesfully stored to database")

            except Exception as e:
                print(f"{stock}: Error ({e})")


def create_directory(directory):
    # Check whether the specified path exists or not
    directory_exist = os.path.exists(directory)

    if not directory_exist:
        os.makedirs(directory, exist_ok=True)


def main():
    """Run fundamental analysis scraper"""
    stockbit_scraper = StockbitScraper()

    # Login
    username = os.environ["STOCKBIT_USERNAME"]
    password = os.environ["STOCKBIT_PASSWORD"]

    stockbit_scraper.login(username, password)

    # Get list of stocks
    ALL = pd.read_csv("./src/stock_analysis/static/20230402_stocks_list.csv", index_col=0).index.to_list()

    # Get fundamental data
    stockbit_scraper.get_statement_release_dates(stock_filter=ALL[int(5 * len(ALL) / 7) : int(6 * len(ALL) / 7)])

if __name__ == "__main__":
    main()
