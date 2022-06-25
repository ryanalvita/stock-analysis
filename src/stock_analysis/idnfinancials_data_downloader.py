import os
from time import sleep
from typing import Optional

import pandas as pd
import requests
from alive_progress import alive_bar
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from stock_analysis.google_drive_api import GoogleDriveAPI

IDX_30 = ["ADRO","ANTM","ASII","BBCA","BBNI","BBRI","BBTN","BMRI","BRPT","BUKA","CPIN","EMTK","EXCL","ICBP","INCO","INDF","INKP","KLBF","MDKA","MIKA","PGAS","PTBA","SMGR","TBIG","TINS","TLKM","TOWR","UNTR","UNVR","WSKT"]
LQ_45 = ["ADRO","AMRT","ANTM","ASII","BBCA","BBNI","BBRI","BBTN","BFIN","BMRI","BRPT","BUKA","CPIN","EMTK","ERAA","EXCL","GGRM","HMSP","HRUM","ICBP","INCO","INDF","INKP","INTP","ITMG","JPFA","KLBF","MDKA","MEDC","MIKA","MNCN","PGAS","PTBA","PTPP","SMGR","TBIG","TINS","TKIM","TLKM","TOWR","TPIA","UNTR","UNVR","WIKA","WSKT"]
IDX_80 = ["AALI","ACES","ADRO","AGII","AKRA","AMRT","ANTM","ASII","ASRI","ASSA","BBCA","BBNI","BBRI","BBTN","BFIN","BJBR","BJTM","BMRI","BMTR","BRPT","BSDE","BTPS","BUKA","CPIN","CTRA","DGNS","DMAS","DOID","DSNG","ELSA","EMTK","ERAA","ESSA","EXCL","GGRM","HEAL","HMSP","HOKI","HRUM","ICBP","INCO","INDF","INKP","INTP","ISAT","ITMG","JPFA","JSMR","KAEF","KLBF","LPKR","LPPF","LSIP","MAPI","MDKA","MEDC","MIKA","MNCN","MYOR","PGAS","PTBA","PTPP","PWON","SCMA","SIDO","SMGR","SMRA","SRTG","TAPG","TBIG","TINS","TKIM","TLKM","TOWR","TPIA","UNTR","UNVR","WIKA","WMUU","WSKT"]

ALL = ['AALI', 'ABBA', 'ABMM', 'ACES', 'ACST', 'ADCP', 'ADES', 'ADHI', 'ADMF', 'ADMG', 'ADMR', 'ADRO', 'AGAR', 'AGII', 'AGRO', 'AGRS', 'AHAP', 'AIMS', 'AISA', 'AKKU', 'AKPI', 'AKRA', 'AKSI', 'ALDO', 'ALKA', 'ALMI', 'ALTO', 'AMAG', 'AMAN', 'AMAR', 'AMFG', 'AMIN', 'AMOR', 'AMRT', 'ANDI', 'ANJT', 'ANTM', 'APEX', 'APIC', 'APII', 'APLI', 'APLN', 'ARCI', 'ARGO', 'ARII', 'ARKA', 'ARNA', 'ARTA', 'ARTO', 'ASBI', 'ASDM', 'ASGR', 'ASHA', 'ASII', 'ASJT', 'ASLC', 'ASMI', 'ASPI', 'ASRI', 'ASRM', 'ASSA', 'ATAP', 'ATIC', 'AUTO', 'AVIA', 'AYLS', 'BABP', 'BACA', 'BAJA', 'BALI', 'BANK', 'BAPA', 'BAPI', 'BATA', 'BAUT', 'BAYU', 'BBCA', 'BBHI', 'BBKP', 'BBLD', 'BBMD', 'BBNI', 'BBRI', 'BBRM', 'BBSI', 'BBSS', 'BBTN', 'BBYB', 'BCAP', 'BCIC', 'BCIP', 'BDMN', 'BEBS', 'BEEF', 'BEKS', 'BELL', 'BESS', 'BEST', 'BFIN', 'BGTG', 'BHAT', 'BHIT', 'BIKA', 'BIKE', 'BIMA', 'BINA', 'BINO', 'BIPI', 'BIPP', 'BIRD', 'BISI', 'BJBR', 'BJTM', 'BKDP', 'BKSL', 'BKSW', 'BLTA', 'BLTZ', 'BLUE', 'BMAS', 'BMHS', 'BMRI', 'BMTR', 'BNBA', 'BNBR', 'BNGA', 'BNII', 'BNLI', 'BOBA', 'BOGA', 'BOLA', 'BOLT', 'BOSS', 'BPFI', 'BPTR', 'BRIS', 'BRMS', 'BRPT', 'BSDE', 'BSIM', 'BSML', 'BSSR', 'BTEK', 'BTON', 'BTPN', 'BTPS', 'BUDI', 'BUKA', 'BUKK', 'BULL', 'BUMI', 'BVIC', 'BWPT', 'BYAN', 'CAKK', 'CAMP', 'CANI', 'CARE', 'CARS', 'CASA', 'CASH', 'CASS', 'CBMF', 'CCSI', 'CEKA', 'CENT', 'CFIN', 'CINT', 'CITA', 'CITY', 'CLEO', 'CLPI', 'CMNP', 'CMNT', 'CMPP', 'CMRY', 'CNKO', 'CNTX', 'COCO', 'CPIN', 'CPRO', 'CSAP', 'CSIS', 'CSMI', 'CSRA', 'CTRA', 'DADA', 'DART', 'DAYA', 'DCII', 'DEAL', 'DEPO', 'DEWA', 'DFAM', 'DGIK', 'DGNS', 'DIGI', 'DILD', 'DIVA', 'DKFT', 'DLTA', 'DMAS', 'DMMX', 'DMND', 'DNAR', 'DNET', 'DOID', 'DPNS', 'DRMA', 'DSFI', 'DSNG', 'DUTI', 'DVLA', 'DWGL', 'DYAN', 'EAST', 'ECII', 'EDGE', 'EKAD', 'ELSA', 'ELTY', 'EMDE', 'EMTK', 'ENAK', 'ENRG', 'ENZO', 'EPAC', 'EPMT', 'ERAA', 'ERTX', 'ESIP', 'ESSA', 'ESTA', 'ESTI', 'EXCL', 'FAPA', 'FAST', 'FILM', 'FIMP', 'FIRE', 'FISH', 'FITT', 'FLMC', 'FMII', 'FOOD', 'FORU', 'FPNI', 'FREN', 'FUJI', 'GAMA', 'GDST', 'GDYR', 'GEMA', 'GEMS', 'GGRM', 'GGRP', 'GHON', 'GJTL', 'GLOB', 'GLVA', 'GMFI', 'GOLD', 'GOOD', 'GOTO', 'GPRA', 'GPSO', 'GSMF', 'GTSI', 'GWSA', 'GZCO', 'HAIS', 'HDFA', 'HDIT', 'HEAL', 'HELI', 'HERO', 'HEXA', 'HITS', 'HKMU', 'HMSP', 'HOKI', 'HOMI', 'HOPE', 'HRME', 'HRTA', 'HRUM', 'IATA', 'IBOS', 'IBST', 'ICBP', 'ICON', 'IDEA', 'IDPR', 'IFII', 'IFSH', 'IGAR', 'IKAN', 'IKBI', 'IMAS', 'IMJS', 'IMPC', 'INAF', 'INAI', 'INCF', 'INCI', 'INCO', 'INDF', 'INDO', 'INDR', 'INDS', 'INDX', 'INDY', 'INKP', 'INOV', 'INPC', 'INPP', 'INPS', 'INRU', 'INTD', 'INTP', 'IPAC', 'IPCC', 'IPCM', 'IPOL', 'IPPE', 'IPTV', 'IRRA', 'ISAT', 'ISSP', 'ITIC', 'ITMA', 'ITMG', 'JAST', 'JAWA', 'JAYA', 'JECC', 'JIHD', 'JKON', 'JMAS', 'JPFA', 'JRPT', 'JSKY', 'JSMR', 'JTPE', 'KAEF', 'KARW', 'KAYU', 'KBAG', 'KBLI', 'KBLM', 'KBLV', 'KDSI', 'KEEN', 'KEJU', 'KIAS', 'KICI', 'KIJA', 'KINO', 'KIOS', 'KJEN', 'KKGI', 'KLBF', 'KMDS', 'KMTR', 'KOBX', 'KOIN', 'KONI', 'KOPI', 'KOTA', 'KPIG', 'KRAS', 'KREN', 'KUAS', 'LABA', 'LAND', 'LCKM', 'LEAD', 'LFLO', 'LINK', 'LION', 'LMAS', 'LMPI', 'LMSH', 'LPCK', 'LPGI', 'LPIN', 'LPKR', 'LPLI', 'LPPF', 'LPPS', 'LSIP', 'LTLS', 'LUCK', 'LUCY', 'MAIN', 'MAPA', 'MAPI', 'MARI', 'MARK', 'MASA', 'MASB', 'MAYA', 'MBAP', 'MBSS', 'MBTO', 'MCAS', 'MCOL', 'MCOR', 'MDIA', 'MDKA', 'MDKI', 'MDLN', 'MEDC', 'MEGA', 'MERK', 'META', 'MFIN', 'MFMI', 'MGLV', 'MGRO', 'MICE', 'MIDI', 'MIKA', 'MIRA', 'MITI', 'MKNT', 'MKPI', 'MLBI', 'MLIA', 'MLPL', 'MLPT', 'MMLP', 'MNCN', 'MOLI', 'MPMX', 'MPOW', 'MPPA', 'MPRO', 'MRAT', 'MREI', 'MSIN', 'MSKY', 'MTDL', 'MTEL', 'MTLA', 'MTMH', 'MTPS', 'MTSM', 'MTWI', 'MYOH', 'MYOR', 'MYTX', 'NANO', 'NASA', 'NASI', 'NATO', 'NELY', 'NETV', 'NFCX', 'NICK', 'NICL', 'NIKL', 'NIRO', 'NISP', 'NOBU', 'NPGF', 'NRCA', 'NTBK', 'NZIA', 'OASA', 'OBMD', 'OILS', 'OKAS', 'OLIV', 'OMRE', 'OPMS', 'PADI', 'PALM', 'PAMG', 'PANI', 'PANR', 'PANS', 'PBID', 'PBRX', 'PBSA', 'PCAR', 'PDES', 'PEGE', 'PEHA', 'PGAS', 'PGJO', 'PGLI', 'PGUN', 'PICO', 'PJAA', 'PKPK', 'PLAN', 'PLIN', 'PMJS', 'PMMP', 'PNBN', 'PNBS', 'PNGO', 'PNIN', 'PNLF', 'POLA', 'POLI', 'POLL', 'POLU', 'POLY', 'POWR', 'PPGL', 'PPRE', 'PPRO', 'PRAS', 'PRDA', 'PRIM', 'PSAB', 'PSDN', 'PSGO', 'PSKT', 'PSSI', 'PTBA', 'PTDU', 'PTIS', 'PTPP', 'PTPW', 'PTRO', 'PTSN', 'PUDP', 'PURA', 'PURE', 'PURI', 'PWON', 'PYFA', 'PZZA', 'RAJA', 'RALS', 'RANC', 'RBMS', 'RDTX', 'REAL', 'RELI', 'RICY', 'RIGS', 'RISE', 'RMKE', 'ROCK', 'RODA', 'ROTI', 'RSGK', 'RUIS', 'RUNS', 'SAFE', 'SAME', 'SAMF', 'SAPX', 'SATU', 'SBAT', 'SBMA', 'SCCO', 'SCMA', 'SCNP', 'SDMU', 'SDPC', 'SDRA', 'SEMA', 'SFAN', 'SGER', 'SGRO', 'SHID', 'SHIP', 'SICO', 'SIDO', 'SILO', 'SIMP', 'SINI', 'SIPD', 'SKBM', 'SKLT', 'SKRN', 'SLIS', 'SMAR', 'SMBR', 'SMCB', 'SMDM', 'SMDR', 'SMGR', 'SMKL', 'SMKM', 'SMMT', 'SMRA', 'SMSM', 'SNLK', 'SOCI', 'SOFA', 'SOHO', 'SOSS', 'SOTS', 'SPMA', 'SPTO', 'SQMI', 'SRAJ', 'SRSN', 'SRTG', 'SSIA', 'SSMS', 'SSTM', 'STAA', 'STAR', 'STTP', 'SULI', 'SWAT', 'TALF', 'TAMA', 'TAPG', 'TAXI', 'TAYS', 'TBIG', 'TBLA', 'TBMS', 'TCID', 'TCPI', 'TEBE', 'TECH', 'TELE', 'TFAS', 'TGKA', 'TGRA', 'TIFA', 'TINS', 'TIRA', 'TIRT', 'TKIM', 'TLDN', 'TLKM', 'TMAS', 'TMPO', 'TNCA', 'TOBA', 'TOPS', 'TOTL', 'TOTO', 'TOWR', 'TOYS', 'TPIA', 'TPMA', 'TRIM', 'TRIN', 'TRIS', 'TRJA', 'TRST', 'TRUE', 'TRUK', 'TRUS', 'TSPC', 'TUGU', 'UANG', 'UCID', 'UFOE', 'ULTJ', 'UNIC', 'UNIQ', 'UNSP', 'UNTR', 'UNVR', 'URBN', 'UVCR', 'VICI', 'VICO', 'VINS', 'VIVA', 'VOKS', 'VRNA', 'WAPO', 'WEGE', 'WEHA', 'WGSH', 'WICO', 'WIFI', 'WIIM', 'WIKA', 'WINR', 'WINS', 'WIRG', 'WMPP', 'WMUU', 'WOMF', 'WOOD', 'WOWS', 'WSKT', 'WTON', 'YELO', 'YPAS', 'YULE', 'ZBRA', 'ZINC', 'ZONE', 'ZYRX']

class IDNFinancials_Downloader:
    def __init__(self,
                 target_url='https://www.idnfinancials.com/'):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("start-maximized"); # open Browser in maximized mode
        chrome_options.add_argument("disable-infobars"); # disabling infobars
        chrome_options.add_argument("--disable-dev-shm-usage"); # overcome limited resource problems
        chrome_options.add_argument("--disable-extensions"); # disabling extensions
        chrome_options.add_argument("--disable-gpu"); # applicable to windows os only
        chrome_options.add_argument("--no-sandbox"); # bypass OS security model
        chrome_options.add_argument("--headless"); # bypass OS security model
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

        self.target_url = target_url
        self.driver.get(self.target_url)

        # Create directory
        self.directory = f"./results/idnfinancials"
        create_directory(self.directory)

        # Get google drive API
        # Initialize google drive api
        self.gdrive_api = GoogleDriveAPI()

    def get_all_companies_url(self, stocks_filter: Optional[list] = None):
        # Get company page
        self.driver.get(self.target_url + "/company")

        # Get maximum_page
        max_page = int(
            self.driver.find_element(
                By.XPATH, '//*[@id="content"]/div/div/div[1]/div[3]/ul/li[5]/a'
            ).get_attribute("data-ci-pagination-page")
        )

        # Get companies url
        all_companies_url = pd.DataFrame()
        print(f"Getting all companies url in progress: {max_page} pages")
        with alive_bar(max_page, force_tty=True) as bar:
            for page in range(1, max_page + 1):
                self.driver.get(f"https://www.idnfinancials.com/company/page/{page}")

                # Get urls of all companies
                for element in self.driver.find_elements(
                    By.XPATH, '//*[@id="table-companies"]/div[2]/div'
                ):
                    stock_code = element.find_element(By.CLASS_NAME, "code").text
                    if stocks_filter:
                        if stock_code in stocks_filter:
                            continue
                    url = element.find_element(By.CLASS_NAME, "ld").get_attribute(
                        "href"
                    )

                    all_companies_url.loc[stock_code, "Url"] = url

                bar()

        # Save overview companies data as csv
        all_companies_url.to_csv(f"{self.directory}/all_companies_url.csv")

        # Upload to google drive
        folder_id = os.environ["GDRIVE_FOLDER_ID_IDNFINANCIALS"]

        # Update previous version
        try:
            query = f"name = 'all_companies_url.csv' and '{folder_id}' in parents"
            file_id = self.gdrive_api.file_list(query)[0].get("id")
            self.gdrive_api.file_update(f'{self.directory}/all_companies_url.csv', file_id)
        # Create new file
        except:
            self.gdrive_api.file_upload(f"{self.directory}/all_companies_url.csv", folder_id)


    def get_all_financials_url(self):
        # Load all_companies_url
        all_companies_url = pd.read_csv(
            f"{self.directory}/all_companies_url.csv", index_col=0
        )

        # Get financials url
        all_financials_url = pd.DataFrame()
        print(f"Getting financials url in progress: {len(all_companies_url)} companies")
        with alive_bar(len(all_companies_url), force_tty=True) as bar:
            for stock_code, company_url in all_companies_url.iterrows():
                # Get company page
                self.driver.get(company_url[0] + "/documents")
                sleep(3)

                financial_years = self.driver.find_elements(
                    By.XPATH, '//*[@id="table-reports"]/tbody/tr'
                )
                for financial_year in financial_years:
                    year = financial_year.find_element(
                        By.XPATH, './td[@class="w-25 text-center"]'
                    ).text
                    financial_urls = financial_year.find_elements(
                        By.XPATH, './td/a[@target="_blank"]'
                    )
                    for financial_url in financial_urls:
                        period = financial_url.find_element(By.XPATH, "./span").text
                        url = financial_url.get_attribute("href")

                        financial_url = pd.Series(dtype=object)
                        financial_url["Stock Code"] = stock_code
                        financial_url["Year"] = year
                        financial_url["Period"] = period
                        financial_url["Url"] = url

                        all_financials_url = pd.concat(
                            [all_financials_url, financial_url],
                            axis=1,
                            ignore_index=True,
                        )
                bar()

        # Transpose the dataframe
        all_financials_url = all_financials_url.T

        # Save overview companies data as csv
        all_financials_url.to_csv(f"{self.directory}/all_financials_url.csv")

        # Upload to google drive
        folder_id = os.environ["GDRIVE_FOLDER_ID_IDNFINANCIALS"]

        # Update previous version
        try:
            query = f"name = 'all_financials_url.csv' and '{folder_id}' in parents"
            file_id = self.gdrive_api.file_list(query)[0].get("id")
            self.gdrive_api.file_update(f'{self.directory}/all_financials_url.csv', file_id)
        # Create new file
        except:
            self.gdrive_api.file_upload(f"{self.directory}/all_financials_url.csv", folder_id)

    def download_data(
        self,
        stock_filter: Optional[list] = None,
        year_filter: Optional[list] = None,
        period_filter: Optional[list] = None,
    ):
        # Get financials url
        all_financials_url = pd.read_csv(f"{self.directory}/all_financials_url.csv", index_col=0)

        # Filter
        if stock_filter:
            if isinstance(stock_filter, str):
                stock_filter = list(stock_filter.split(","))
            all_financials_url = all_financials_url[
                all_financials_url["Stock Code"].isin(stock_filter)
            ]
        if year_filter:
            if isinstance(year_filter, str):
                year_filter = list(year_filter.split(","))
            all_financials_url = all_financials_url[
                all_financials_url["Year"].isin(year_filter)
            ]
        if period_filter:
            if isinstance(period_filter, str):
                period_filter = list(period_filter.split(","))
            all_financials_url = all_financials_url[
                all_financials_url["Period"].isin(period_filter)
            ]

        with alive_bar(len(all_financials_url), force_tty=True) as bar:
            for ix, row in all_financials_url.iterrows():
                stock_code = row["Stock Code"]
                year = row["Year"]
                period = row["Period"]
                url = row["Url"]

                directory = f"{self.directory}/{stock_code}"
                create_directory(directory)

                filepath = (
                    f"{directory}/{year}_{period}_{stock_code}_Financial_Statement.pdf"
                )

                try:
                    response = requests.get(url)
                    file = open(filepath, "wb")
                    file.write(response.content)
                    file.close()

                    # Upload to google drive
                    parents_folder_id = os.environ["GDRIVE_FOLDER_ID_IDNFINANCIALS"]
                    folder_name = stock_code

                    # Create folder if it doesn't exist
                    try:
                        query = f"name = '{folder_name}' and '{parents_folder_id}' in parents"
                        folder_id = self.gdrive_api.file_list(query)[0].get("id")
                    except:
                        self.gdrive_api.create_folder(folder_name, parents_folder_id)
                        query = f"name = '{folder_name}' and '{parents_folder_id}' in parents"
                        folder_id = self.gdrive_api.file_list(query)[0].get("id")
                        print(f"New folder of {stock_code} has been created")
                        
                    # Update
                    try:
                        query = f"name = '{directory}/{year}_{period}_{stock_code}_Financial_Statement.pdf' and '{folder_id}' in parents"
                        print(f"Financial statement of {stock_code} {period} {year} is already exist.")
                        continue
                    except:
                        self.gdrive_api.file_upload(f"{directory}/{year}_{period}_{stock_code}_Financial_Statement.pdf", folder_id)

                except:
                    print(
                        f"Error on stock_code = {stock_code}, year = {year}, period = {period}, ix = {ix}"
                    )

                bar()

        print(f"All financial statement is downloaded and stored in: {directory} directory")

def create_directory(directory):
    # Check whether the specified path exists or not
    directory_exist = os.path.exists(directory)

    if not directory_exist:
        os.makedirs(directory, exist_ok=True)

def main():
    """Run idn finacials downloader"""
    idnfinancials_scraper = IDNFinancials_Downloader()

    # Get all companies url
    idnfinancials_scraper.get_all_companies_url()

    # Get all financials url
    idnfinancials_scraper.get_all_financials_url()

    # Download financial statement
    idnfinancials_scraper.download_data()

if __name__ == '__main__':
    main()
