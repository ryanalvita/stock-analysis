import os
import pandas as pd
import smtplib

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager


class NotifikasiEmailRilisLapkeu:
    def __init__(self):
                 
        chrome_options = webdriver.ChromeOptions()
        # open Browser in maximized mode
        chrome_options.add_argument("start-maximized");
        # disabling infobars
        chrome_options.add_argument("disable-infobars");
        # overcome limited resource problems
        chrome_options.add_argument("--disable-dev-shm-usage");
        # disabling extensions
        chrome_options.add_argument("--disable-extensions");
        # disabling gpu, applicable to windows os only
        chrome_options.add_argument("--disable-gpu");
        # bypass OS security model
        chrome_options.add_argument("--no-sandbox");
        chrome_options.add_argument("--headless");

        self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

    def get_all_releases(
        self,
    ):
        # Define url
        url = 'https://idx.co.id/perusahaan-tercatat/keterbukaan-informasi/'
        
        # Go to url
        self.driver.get(url)
        sleep(3)

        # Fill keyword
        self.driver.find_element(By.ID, 'keywordInput').send_keys("Laporan Keuangan")

        # Click search
        period_click = self.driver.find_element(By.ID, 'searchBtn')
        self.driver.execute_script("arguments[0].click();", period_click)
        sleep(2)

        # Datetime now
        datetime_now = datetime.now()
        datetime_now = datetime_now.replace(hour= 0, minute=0, second=0, microsecond=0)
        datetime_yesterday = datetime_now - pd.DateOffset(1)

        df = pd.DataFrame()

        while True:
            sleep(1)
            elements = self.driver.find_elements(By.XPATH, "/html/body/main/div[2]/div/div[2]/div/div")
            i = 1
            for element in elements:
                texts = element.text.split("\n")
                time = datetime.strptime(texts[0], "%d %B %Y %H:%M:%S")
                if time < datetime_yesterday:
                    break
                elif time.day == datetime_yesterday.day:
                    try: 
                        text_lapkeu = [text for text in texts if 'Penyampaian Laporan Keuangan' in text][0]
                        
                        ticker = text_lapkeu[-6:-2]
                        text_financial = [text for text in texts if 'FinancialStatement' in text][0].split('-')
                        quarter = text_financial[2]
                        year = text_financial[1]

                        link = self.driver.find_element(By.XPATH, f'/html/body/main/div[2]/div/div[2]/div/div[{i}]/a').get_attribute('href')

                        df.loc[ticker, "Quarter"] = quarter
                        df.loc[ticker, "Year"] = year
                        df.loc[ticker, "Link"] = link
                        
                        i += 1
                    except:
                        i += 1
                        continue

            # Break if time is less than yesterday
            if time < datetime_yesterday:
                break
            else:
                # Continue to next page
                period_click = self.driver.find_element(By.XPATH, '/html/body/main/div[2]/div/dir-pagination-controls/ul/li[11]/a')
                self.driver.execute_script("arguments[0].click();", period_click)

        # Store to df
        self.df = df

    def send_email(
        self,
    ):
        # Construct HTML
        with open("./src/stock_analysis/html_template.html", "r", encoding='utf-8') as f:
            html = f.read()
        
        insert = []

        for ix, row in self.df.iterrows():
            if row["Quarter"] == "I":
                quarter = "Q1"
            elif row["Quarter"] == "II":
                quarter = "Q2"
            elif row["Quarter"] == "III":
                quarter = "Q3"
            elif row["Quarter"] == "Tahunan":
                quarter = "FY"

            number = ix + 1
            ticker = row["Unnamed: 0"]
            year = row["Year"]
            link = row["Link"]
            insert.append(f'<tr>\n                      <td align="left" style="padding:10px;Margin:0"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, \'helvetica neue\', helvetica, sans-serif;line-height:27px;color:#333333;font-size:18px"><strong>{number}. {ticker} [{quarter} - {year}]</strong><br><a target="_blank" href="{link}" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;text-decoration:underline;color:#1376C8;font-size:18px;font-family:arial, \'helvetica neue\', helvetica, sans-serif">Link</a></p></td>\n                     </tr>\n                     ')

        html = html.replace('<tr>\n                      <td align="left" style="padding:10px;Margin:0"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, \'helvetica neue\', helvetica, sans-serif;line-height:27px;color:#333333;font-size:18px"><strong>1. BBRI [Q2 - 2022]</strong><br><a target="_blank" href="https://www.idnfinancials.com/bbri" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;text-decoration:underline;color:#1376C8;font-size:18px;font-family:arial, \'helvetica neue\', helvetica, sans-serif"><u>https://www.idnfinancials.com/bbri</u></a></p></td>\n                     </tr>\n                     <tr>\n                      <td align="left" style="padding:10px;Margin:0"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, \'helvetica neue\', helvetica, sans-serif;line-height:27px;color:#333333;font-size:18px"><strong>2. UNVR [Q2 - 2022]</strong><br><a target="_blank" href="https://www.idnfinancials.com/unvr" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;text-decoration:underline;color:#1376C8;font-size:18px;font-family:arial, \'helvetica neue\', helvetica, sans-serif">https://www.idnfinancials.com/unvr</a></p></td>\n                     </tr>\n                     <tr>\n                      <td align="left" style="padding:10px;Margin:0"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, \'helvetica neue\', helvetica, sans-serif;line-height:27px;color:#333333;font-size:18px"><strong>3. TLKM [Q2 - 2022]</strong><br><a target="_blank" href="https://www.idnfinancials.com/tlkm" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;text-decoration:underline;color:#1376C8;font-size:18px;font-family:arial, \'helvetica neue\', helvetica, sans-serif">https://www.idnfinancials.com/tlkm</a></p></td>\n                     </tr>\n                   </table></td>\n                 </tr>\n               ', ''.join(insert))
        
        datetime_now = datetime.now()
        datetime_now = datetime_now.replace(hour= 0, minute=0, second=0, microsecond=0)
        datetime_yesterday = datetime_now - pd.DateOffset(1)

        html = html.replace('1 Oktober 2020', datetime.strftime(datetime_yesterday, "%d %B %Y"))

        # Send email
        # sender
        yahoo_email = (os.environ["YAHOO_ID"])
        yahoo_password = (os.environ["YAHOO_PASSWORD"])

        # reciever
        email_from = yahoo_email
        email_to = (os.environ["GMAIL_ID"])

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Notifikasi Rilis Laporan Keuangan"
        msg['From'] = email_from
        msg['To'] = email_to

        # Record the MIME types
        part = MIMEText(html, 'html')

        # Attach parts into message container.
        msg.attach(part)

        server = smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465)
        server.ehlo()
        server.login(yahoo_email, yahoo_password)
        server.sendmail(email_from, email_to, msg.as_string())
        server.quit()

def main():
    """Get"""
    main_class = NotifikasiEmailRilisLapkeu()

    # Get all stock code
    main_class.get_all_releases()

    # Send email
    main_class.send_email()

if __name__ == '__main__':
    main()