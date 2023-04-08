from datetime import datetime
from time import sleep

import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def main():
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
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(
        ChromeDriverManager().install(), chrome_options=chrome_options
    )

    results = {}
    # First URL (2017-forward)
    years = [2022, 2021, 2020, 2019, 2018]
    for year in years:
        if year in [2018, 2019]:
            url = f"https://doktersaham.com/saham/indeks-saham/lq45-febuari-juli-{year}"
        elif year in [2021]:
            url = f"https://doktersaham.com/saham/indeks-saham/indeks-lq45-februari-{year}-januari-{year}"
        else:
            url = f"https://doktersaham.com/saham/indeks-saham/indeks-lq45-februari-{year}-juli-{year}"

        stocks_list = []
        for page in [1, 2, 3]:
            page_url = url + f"?page={page}"
            try:
                # Go to url
                driver.get(page_url)
                sleep(1)
            except Exception:
                print(f"Cannot access url: {page_url}")
        
            elements = driver.find_elements(By.XPATH, '/html/body/div/div[1]/div[2]/div/div[1]/div[2]/table/tbody/tr/td[2]')
            stocks_list.extend([element.text for element in elements])
            
        results[year] = stocks_list

    # Second URL (2017 - backwards)
    url = "https://www.sahamok.net/bei/lq-45/"

    try:
        # Go to url
        driver.get(url)
        sleep(2)
    except Exception:
        print(f"Cannot access url: {url}")

    elements = driver.find_elements(By.XPATH, '//*[@id="post-6846"]/div/div/table/tbody/tr/td[3]/a')
    urls = [element.get_attribute('href') for element in elements]
    elements = driver.find_elements(By.XPATH, '/html/body/div[1]/div/div/div[1]/div/article/div/div/table/tbody/tr/td[3]/a')
    years = [element.text[:4] for element in elements]
    for (url, year) in zip(urls, years):
        try:
            # Go to url
            driver.get(url)
            sleep(1)
        except Exception:
            print(f"Cannot access url: {url}")
        elements = driver.find_elements(By.XPATH, '/html/body/div[1]/div/div/div[1]/div/article/div/div/table[1]/tbody/tr/td[2]')
        stocks_list = [element.text for element in elements]
        
        if driver.find_elements(By.XPATH, '/html/body/div[1]/div/div/div[1]/div/article/div/div/table[3]/tbody/tr/td[2]'):
            elements = driver.find_elements(By.XPATH, '/html/body/div[1]/div/div/div[1]/div/article/div/div/table[2]/tbody/tr/td[2]')
            stocks_list.extend([element.text for element in elements])

        stocks_list = [stock.replace(" ", "") for stock in stocks_list if (stock != "Kode Saham") & (stock != "Emiten") & (stock != "Kode")]
        results[year] = stocks_list

    date_now = (
        datetime.now()
        .timestamp()
    )
    pd.DataFrame(results).to_csv(f'{date_now}_stocks_list_LQ45.csv')

if __name__ == "__main__":
    main()
