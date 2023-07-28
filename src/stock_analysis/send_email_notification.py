import os
import pandas as pd
import smtplib, ssl

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pymongo import MongoClient
from stock_analysis.utils import clean_dataframe


class NotifikasiEmailRilisLapkeu:
    def __init__(self):
        # Initialize MongoDB
        self.cluster = MongoClient(os.environ["MONGODB_URI"])
        self.db = self.cluster["stockbit_data"]
        self.collection = self.db["release_date"]
        self.collection_quarterly = self.db["quarterly"]

        self.dt_now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.dt_yesterday = self.dt_now - pd.DateOffset(days=1)

    def send_email(
        self,
    ):
        # Construct HTML
        with open(
            "./src/stock_analysis/html_template.html", "r", encoding="utf-8"
        ) as f:
            html = f.read()

        number = 1

        insert = []
        for element in self.collection.find({"latest.release_date": self.dt_yesterday}):
            code = element["stock_code"]
            year = element["latest"]["year"]
            quarter = element["latest"]["quarter"]
            link = f"https://www.idx.co.id/id/perusahaan-tercatat/profil-perusahaan-tercatat/{code}"

            # Load data
            data = self.collection_quarterly.find_one({"stock_code": code})
            df = clean_dataframe(pd.DataFrame(data["income_statement"]))
            df = df.loc[:, ::-1]

            # extract the year from column names and create a year column
            df = df.groupby(lambda x: x[-4:], axis=1).apply(lambda x: x.cumsum(axis=1))

            # Shift the data by 4 periods (one year)
            df_shifted = df.shift(4, axis=1)
            growth = (df - df_shifted) / df_shifted * 100
            df.loc["QoQ YTD Net Income Growth"] = growth.loc["Total Net Income Attributable To"]

            for data in self.collection_quarterly.find({"stock_code": code}):
                if data["income_statement"].get(f"{quarter} {year}"):
                    ni_growth_ytd_yoy = round(df[f"{quarter} {year}"]["QoQ YTD Net Income Growth"], 2)
                    if ni_growth_ytd_yoy > 0:
                        text_color = '#008000'
                        symbol = '▲'
                    else:
                        text_color = '#FF0000'
                        symbol = '▼'
                    growth_html = f'<br>Net Income YTD YoY: <span style="color:{text_color};"><strong>+{ni_growth_ytd_yoy}% {symbol}</strong></span></br>'
                else:
                    growth_html = '<br>Data is not available yet</br>'

            insert.append(
                f'<tr>\n                      <td align="left" style="padding:10px;Margin:0"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, \'helvetica neue\', helvetica, sans-serif;line-height:27px;color:#333333;font-size:18px"><strong>{number}. {code} [{quarter} - {year}]</strong><br><a target="_blank" href="{link}" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;text-decoration:underline;color:#1376C8;font-size:18px;font-family:arial, \'helvetica neue\', helvetica, sans-serif">Link</a></br>{growth_html}</p></td>\n                     </tr>\n                     '
            )

            number += 1

        if len(insert) != 0:
            html = html.replace(
                '<tr>\n                      <td align="left" style="padding:10px;Margin:0"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, \'helvetica neue\', helvetica, sans-serif;line-height:27px;color:#333333;font-size:18px"><strong>1. BBRI [Q2 - 2022]</strong><br><a target="_blank" href="https://www.idnfinancials.com/bbri" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;text-decoration:underline;color:#1376C8;font-size:18px;font-family:arial, \'helvetica neue\', helvetica, sans-serif"><u>https://www.idnfinancials.com/bbri</u></a></p></td>\n                     </tr>\n                     <tr>\n                      <td align="left" style="padding:10px;Margin:0"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, \'helvetica neue\', helvetica, sans-serif;line-height:27px;color:#333333;font-size:18px"><strong>2. UNVR [Q2 - 2022]</strong><br><a target="_blank" href="https://www.idnfinancials.com/unvr" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;text-decoration:underline;color:#1376C8;font-size:18px;font-family:arial, \'helvetica neue\', helvetica, sans-serif">https://www.idnfinancials.com/unvr</a></p></td>\n                     </tr>\n                     <tr>\n                      <td align="left" style="padding:10px;Margin:0"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, \'helvetica neue\', helvetica, sans-serif;line-height:27px;color:#333333;font-size:18px"><strong>3. TLKM [Q2 - 2022]</strong><br><a target="_blank" href="https://www.idnfinancials.com/tlkm" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;text-decoration:underline;color:#1376C8;font-size:18px;font-family:arial, \'helvetica neue\', helvetica, sans-serif">https://www.idnfinancials.com/tlkm</a></p></td>\n                     </tr>\n                   </table></td>\n                 </tr>\n               ',
                "".join(insert),
            )
        else:
            html = html.replace(
                '<tr>\n                      <td align="left" style="padding:10px;Margin:0"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, \'helvetica neue\', helvetica, sans-serif;line-height:27px;color:#333333;font-size:18px"><strong>1. BBRI [Q2 - 2022]</strong><br><a target="_blank" href="https://www.idnfinancials.com/bbri" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;text-decoration:underline;color:#1376C8;font-size:18px;font-family:arial, \'helvetica neue\', helvetica, sans-serif"><u>https://www.idnfinancials.com/bbri</u></a></p></td>\n                     </tr>\n                     <tr>\n                      <td align="left" style="padding:10px;Margin:0"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, \'helvetica neue\', helvetica, sans-serif;line-height:27px;color:#333333;font-size:18px"><strong>2. UNVR [Q2 - 2022]</strong><br><a target="_blank" href="https://www.idnfinancials.com/unvr" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;text-decoration:underline;color:#1376C8;font-size:18px;font-family:arial, \'helvetica neue\', helvetica, sans-serif">https://www.idnfinancials.com/unvr</a></p></td>\n                     </tr>\n                     <tr>\n                      <td align="left" style="padding:10px;Margin:0"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, \'helvetica neue\', helvetica, sans-serif;line-height:27px;color:#333333;font-size:18px"><strong>3. TLKM [Q2 - 2022]</strong><br><a target="_blank" href="https://www.idnfinancials.com/tlkm" style="-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;text-decoration:underline;color:#1376C8;font-size:18px;font-family:arial, \'helvetica neue\', helvetica, sans-serif">https://www.idnfinancials.com/tlkm</a></p></td>\n                     </tr>\n                   </table></td>\n                 </tr>\n               ',
                "".join(['<tr>\n                      <td align="left" style="padding:10px;Margin:0"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, \'helvetica neue\', helvetica, sans-serif;line-height:27px;color:#333333;font-size:12px"><center>Tidak ada laporan keuangan yang dirilis hari ini</center><br></p></td>\n                     </tr>\n                     ']),
            )


        html = html.replace(
            "1 Oktober 2020", datetime.strftime(self.dt_yesterday, "%d %B %Y")
        )

        html = html.replace('                      <td align="center" style="padding:0;Margin:0"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, \'helvetica neue\', helvetica, sans-serif;line-height:21px;color:#FFFFFF;font-size:14px">pahamsaham © 2022</p></td>', 
            f'                      <td align="center" style="padding:0;Margin:0"><p style="Margin:0;-webkit-text-size-adjust:none;-ms-text-size-adjust:none;mso-line-height-rule:exactly;font-family:arial, \'helvetica neue\', helvetica, sans-serif;line-height:21px;color:#FFFFFF;font-size:14px">pahamsaham © {self.dt_now.year}</p></td>')

        # Send email
        # sender
        gmail_id = os.environ["GMAIL_ID"]
        gmail_password = os.environ["GMAIL_PASSWORD"]

        # reciever
        email_from = gmail_id
        email_to = gmail_id

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Notifikasi Rilis Laporan Keuangan"
        msg["From"] = email_from
        msg["To"] = email_to

        # Record the MIME types
        part = MIMEText(html, "html")

        # Attach parts into message container.
        msg.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(gmail_id, gmail_password)
            server.sendmail(email_from, email_to, msg.as_string())
            server.quit()

    def store_artifacts(self):
        latest_release_statements = []
        for element in self.collection.find({"latest.release_date": self.dt_yesterday}):
            latest_release_statements.append(["stock_code"])


def main():
    """Get"""
    main_class = NotifikasiEmailRilisLapkeu()

    # Send email
    main_class.send_email()


if __name__ == "__main__":
    main()
