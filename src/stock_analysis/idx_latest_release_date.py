import os

from datetime import datetime as dt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient
from fake_useragent import UserAgent

id_en_months_mapping = {
    'Januari': 'January',
    'Februari': 'February',
    'Maret': 'March',
    'April': 'April',
    'Mei': 'May',
    'Juni': 'June',
    'Juli': 'July',
    'Agustus': 'August',
    'September': 'September',
    'Oktober': 'October',
    'November': 'November',
    'Desember': 'December'
}

def parse_input(input_string):
    parts = input_string.split('\n')
    code = parts[0]
    date_str = parts[1].split(" | ")[0]
    for indonesian_month, english_month in id_en_months_mapping.items():
        date_str = date_str.replace(indonesian_month, english_month)
    release_date = dt.strptime(date_str, "%d %B %Y")
    return code, release_date

class LatestReleaseDate:
    def __init__(self):

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
        # add user agent
        chrome_options.add_argument(f"user-agent={UserAgent().random}")

        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), chrome_options=chrome_options
        )

        # Initialize MongoDB
        self.cluster = MongoClient(os.environ["MONGODB_URI"])
        self.db = self.cluster["stockbit_data"]

    def get_all_latest_releases(
        self,
    ):
        # Define url
        url = "https://www.idx.co.id/id/perusahaan-tercatat/laporan-keuangan-dan-tahunan"

        # Go to url
        self.driver.get(url)
        sleep(3)

        # Datetime now
        datetime_now = dt.now()
        datetime_now = datetime_now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Periode
        for p in range(1, 4+1):
            if len(self.driver.find_elements(By.XPATH, f'/html/body/div[2]/div/div/div[2]/main/div/div[1]/div[2]/div[1]/div/div[4]/div[{p}]/label/input')) == 0:
                self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/main/div/div[1]/div[1]/button').click()
            self.driver.find_element(By.XPATH, f'/html/body/div[2]/div/div/div[2]/main/div/div[1]/div[2]/div[1]/div/div[4]/div[{p}]/label/input').click()
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/main/div/div[1]/div[2]/div[2]/button[2]').click()
            sleep(2)

            if len(self.driver.find_elements(By.XPATH, '/html/body/div[2]/div/div/div[2]/main/div/div[2]/div/div/span')) == 0:
                # Pages
                pages = len(self.driver.find_elements(By.XPATH, '/html/body/div[2]/div/div/div[2]/main/div/ul[2]/li/select/option'))
                pages_select = Select(
                    self.driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/main/div/ul[2]/li[1]/select')
                )
                for i in range(1, pages + 1):
                    pages_select.select_by_value(str(i))
                    sleep(2)

                    # Find elements
                    elements = self.driver.find_elements(
                        By.XPATH, "/html/body/div[2]/div/div/div[2]/main/div/div[2]/div/div/div[1]"
                    )
                    years = self.driver.find_elements(By.XPATH, "/html/body/div[2]/div/div/div[2]/main/div/div[2]/div/div/table[1]/tbody/tr[2]/td[3]")
                    quarters = self.driver.find_elements(By.XPATH, "/html/body/div[2]/div/div/div[2]/main/div/div[2]/div/div/table[1]/tbody/tr[3]/td[3]")
                    for (element, year, quarter) in zip(elements, years, quarters):
                        code, release_date = parse_input(element.text)
                        year = year.text
                        quarter = quarter.text.replace("TW", "Q").replace("Audit", "Q4")

                        # Store data to mongodb
                        collection = self.db["release_date"]

                        # Define filters based on domain_id
                        filter = {"stock_code": f"{code}"}

                        # Determine values to be updated
                        json_structure = {}
                        json_structure["last_update"] = datetime_now
                        json_structure["latest"] = {}
                        json_structure["latest"]["release_date"] = release_date
                        json_structure["latest"]["quarter"] = quarter
                        json_structure["latest"]["year"] = year
                        data = {"$set": json_structure}

                        # Update values to database
                        collection.update_one(filter=filter, update=data, upsert=True)

def main():
    """Get latest financial statement release date from IDX website"""
    main_class = LatestReleaseDate()

    # Get all stock code
    main_class.get_all_latest_releases()


if __name__ == "__main__":
    main()
