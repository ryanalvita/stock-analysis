import json
import os
import sys
from datetime import datetime
from time import sleep
from typing import Optional

import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient


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
            options=chrome_options,
        )

        # Initialize MongoDB
        self.cluster = MongoClient(os.environ["MONGODB_URI"])
        self.db = self.cluster["stockbit_data"]

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

    def get_fundamental_data(
        self,
        stock_filter: Optional[list] = None,
        year_filter: Optional[list] = None,
        period_filter: Optional[list] = None,
    ):
        date = datetime.now().timestamp()

        # Filter
        if stock_filter:
            if isinstance(stock_filter, str):
                stock_filter = list(stock_filter.split(","))
        if year_filter:
            if isinstance(year_filter, str):
                year_filter = list(year_filter.split(","))
        if period_filter:
            if isinstance(period_filter, str):
                period_filter = list(period_filter.split(","))

        # Define report types
        report_types = ["income-statement", "balance-sheet", "cash-flow"]

        # Define statement types
        statement_types = {
            "1": "quarterly",
            "2": "yearly",
        }

        # Get stocks
        stocks = stock_filter
        for stock in stocks:
            try:
                # Define url
                url = f"https://stockbit.com/#/symbol/{stock}/financials"

                try:
                    # Go to url
                    self.driver.get(url)
                    sleep(4)
                except:
                    print(f"Cannot access fundamental data for stock: {stock}")
                    continue

                selection_report_type = Select(
                    self.driver.find_element(
                        By.XPATH, '//*[@id="financial-header"]/div[2]/select'
                    )
                )
                selection_statement_type = Select(
                    self.driver.find_element(
                        By.XPATH, '//*[@id="financial-header"]/div[3]/select'
                    )
                )

                # Select always EN
                Select(
                    self.driver.find_element(
                        By.XPATH, '//*[@id="financial-header"]/div[6]/select'
                    )
                ).select_by_value("EN")

                for key, values in statement_types.items():
                    json_structure = {"stock_code": f"{stock}"}
                    for report_type in report_types:
                        if report_type == "income-statement":
                            selection_report_type.select_by_value("1")
                        elif report_type == "balance-sheet":
                            if values != "ttm":
                                selection_report_type.select_by_value("2")
                            else:
                                continue
                        elif report_type == "cash-flow":
                            selection_report_type.select_by_value("3")
                        sleep(2)

                        selection_statement_type.select_by_value(key)
                        sleep(2)

                        # Always round to K
                        click = self.driver.find_element(
                            By.XPATH,
                            '//*[@id="financial-header"]/div[7]/div[3]/button[2]',
                        )
                        self.driver.execute_script("arguments[0].click();", click)
                        self.driver.execute_script("arguments[0].click();", click)
                        self.driver.execute_script("arguments[0].click();", click)

                        if report_type == "income-statement":
                            tables = pd.read_html(self.driver.page_source)[2:4]
                        elif report_type == "balance-sheet":
                            tables = pd.read_html(self.driver.page_source)[4:8]
                        elif report_type == "cash-flow":
                            tables = pd.read_html(self.driver.page_source)[2:4]
                        data = pd.DataFrame()
                        for table in tables:
                            df = table.rename(
                                columns={
                                    "In Thousand IDR": "In IDR",
                                    "In Million IDR": "In IDR",
                                    "In Billion IDR": "In IDR",
                                    "In Trillion IDR": "In IDR",
                                    "In Thousand": "In IDR",
                                    "In Million": "In IDR",
                                    "In Billion": "In IDR",
                                    "In Trillion": "In IDR",
                                }
                            )
                            data = pd.concat([data, df], axis=0)
                        data = data.fillna("")
                        data = data.drop_duplicates(subset=["In IDR"])
                        data = data.set_index("In IDR")
                        data.columns = data.columns.str.replace("12M ", "")

                        for col in data.columns:
                            data[col] = data[col].apply(
                                lambda x: str(x)
                                .replace(".", "")
                                .replace(" K", "0")
                                .replace(" M", "0000")
                                .replace(" B", "0000000")
                                .replace(" T", "0000000000")
                                .replace("-", "")
                                .replace(")", "")
                                .replace("(", "-")
                                if any(
                                    [
                                        all([ext in str(x) for ext in ([".", "K"])]),
                                        all([ext in str(x) for ext in ([".", "M"])]),
                                        all([ext in str(x) for ext in ([".", "B"])]),
                                        all([ext in str(x) for ext in ([".", "T"])]),
                                    ]
                                )
                                else str(x)
                                .replace(",", "")
                                .replace(" K", "000")
                                .replace(" M", "000000")
                                .replace(" B", "000000000")
                                .replace(" T", "000000000000")
                                .replace("-", "")
                                .replace(")", "")
                                .replace("(", "-")
                            )

                        if report_type == "income-statement":
                            data = data.rename(
                                index={
                                    "Net Income From Continuing Oper...": "Net Income From Continuing Operations",
                                    "Comprehensive Income Attributab...": "Comprehensive Income Attributabable To",
                                }
                            )
                            data = data[~data.index.duplicated(keep="first")]
                            json_structure.update(
                                {"income_statement": json.loads(data.to_json())}
                            )

                        elif report_type == "balance-sheet":
                            data = data.rename(
                                index={
                                    "Cash And Cash Equivalent...": "Cash And Cash Equivalents",
                                    "Investment In Jointly Co...": "Investment In Jointly Controlled Entities",
                                    "Gross Profit After Joint Ventur...": "Gross Profit After Joint Venture",
                                    "Property, Plant And Equi...": "Property, Plant And Equiment",
                                    "Additional Paid-Up Capit...": "Additional Paid-Up Capital",
                                    "Non-Controlling Interest...": "Non-Controlling Interests",
                                }
                            )
                            data = data[~data.index.duplicated(keep="first")]
                            json_structure.update(
                                {"balance_sheet": json.loads(data.to_json())}
                            )

                        elif report_type == "cash-flow":
                            data = data.rename(
                                index={
                                    "Cash Flows From Operating Activ...": "Cash Flows From Operating Activities",
                                    "Cash Flows From Investing Activ...": "Cash Flows From Investing Activities",
                                    "Cash Flows From Financing Activ...": "Cash Flows From Financing Activities",
                                    "Kas Dan Setara Kas Akhir Period...": "Kas Dan Setara Kas Akhir Periode",
                                    "Net Increase (decrease) In Cash...": "Net Increase (Decrease) In Cash and Cash Equivalents",
                                    "Net Increase (Decrease) In Cash...": "Net Increase (Decrease) In Cash and Cash Equivalents",
                                    "Net Effect Of Changes In Exchan...": "Net Effect Of Changes In Exchange Rate In Cash and Cash Equivalents",
                                }
                            )
                            data = data[~data.index.duplicated(keep="first")]
                            json_structure.update(
                                {"cash_flow": json.loads(data.to_json())}
                            )

                    # Store data to mongodb
                    collection = self.db[values]

                    # Define filters based on domain_id
                    filter = {"stock_code": f"{stock}"}

                    # Determine values to be updated
                    json_structure["date"] = date
                    data = {"$set": json_structure}

                    # Update values to database
                    collection.update_one(filter=filter, update=data, upsert=True)

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
    ALL = pd.read_csv(
        "./src/stock_analysis/static/20230402_stocks_list.csv", index_col=0
    ).index.to_list()

    # Get stocks list
    stocks_list = [item for item in sys.argv[1:]]

    # Get fundamental data
    stockbit_scraper.get_fundamental_data(stock_filter=stocks_list)


if __name__ == "__main__":
    main()
