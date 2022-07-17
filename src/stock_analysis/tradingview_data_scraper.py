import json
import os
from time import sleep
from typing import Optional

import numpy as np
import pandas as pd
from alive_progress import alive_bar
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from stock_analysis.google_drive_api import GoogleDriveAPI

IDX_30 = ["ADRO","ANTM","ASII","BBCA","BBNI","BBRI","BBTN","BMRI","BRPT","BUKA","CPIN","EMTK","EXCL","ICBP","INCO","INDF","INKP","KLBF","MDKA","MIKA","PGAS","PTBA","SMGR","TBIG","TINS","TLKM","TOWR","UNTR","UNVR","WSKT"]
LQ_45 = ["ADRO","AMRT","ANTM","ASII","BBCA","BBNI","BBRI","BBTN","BFIN","BMRI","BRPT","BUKA","CPIN","EMTK","ERAA","EXCL","GGRM","HMSP","HRUM","ICBP","INCO","INDF","INKP","INTP","ITMG","JPFA","KLBF","MDKA","MEDC","MIKA","MNCN","PGAS","PTBA","PTPP","SMGR","TBIG","TINS","TKIM","TLKM","TOWR","TPIA","UNTR","UNVR","WIKA","WSKT"]
IDX_80 = ["AALI","ACES","ADRO","AGII","AKRA","AMRT","ANTM","ASII","ASRI","ASSA","BBCA","BBNI","BBRI","BBTN","BFIN","BJBR","BJTM","BMRI","BMTR","BRPT","BSDE","BTPS","BUKA","CPIN","CTRA","DGNS","DMAS","DOID","DSNG","ELSA","EMTK","ERAA","ESSA","EXCL","GGRM","HEAL","HMSP","HOKI","HRUM","ICBP","INCO","INDF","INKP","INTP","ISAT","ITMG","JPFA","JSMR","KAEF","KLBF","LPKR","LPPF","LSIP","MAPI","MDKA","MEDC","MIKA","MNCN","MYOR","PGAS","PTBA","PTPP","PWON","SCMA","SIDO","SMGR","SMRA","SRTG","TAPG","TBIG","TINS","TKIM","TLKM","TOWR","TPIA","UNTR","UNVR","WIKA","WMUU","WSKT"]

ALL = ['AALI', 'ABBA', 'ABMM', 'ACES', 'ACST', 'ADCP', 'ADES', 'ADHI', 'ADMF', 'ADMG', 'ADMR', 'ADRO', 'AGAR', 'AGII', 'AGRO', 'AGRS', 'AHAP', 'AIMS', 'AISA', 'AKKU', 'AKPI', 'AKRA', 'AKSI', 'ALDO', 'ALKA', 'ALMI', 'ALTO', 'AMAG', 'AMAN', 'AMAR', 'AMFG', 'AMIN', 'AMOR', 'AMRT', 'ANDI', 'ANJT', 'ANTM', 'APEX', 'APIC', 'APII', 'APLI', 'APLN', 'ARCI', 'ARGO', 'ARII', 'ARKA', 'ARNA', 'ARTA', 'ARTO', 'ASBI', 'ASDM', 'ASGR', 'ASHA', 'ASII', 'ASJT', 'ASLC', 'ASMI', 'ASPI', 'ASRI', 'ASRM', 'ASSA', 'ATAP', 'ATIC', 'AUTO', 'AVIA', 'AYLS', 'BABP', 'BACA', 'BAJA', 'BALI', 'BANK', 'BAPA', 'BAPI', 'BATA', 'BAUT', 'BAYU', 'BBCA', 'BBHI', 'BBKP', 'BBLD', 'BBMD', 'BBNI', 'BBRI', 'BBRM', 'BBSI', 'BBSS', 'BBTN', 'BBYB', 'BCAP', 'BCIC', 'BCIP', 'BDMN', 'BEBS', 'BEEF', 'BEKS', 'BELL', 'BESS', 'BEST', 'BFIN', 'BGTG', 'BHAT', 'BHIT', 'BIKA', 'BIKE', 'BIMA', 'BINA', 'BINO', 'BIPI', 'BIPP', 'BIRD', 'BISI', 'BJBR', 'BJTM', 'BKDP', 'BKSL', 'BKSW', 'BLTA', 'BLTZ', 'BLUE', 'BMAS', 'BMHS', 'BMRI', 'BMTR', 'BNBA', 'BNBR', 'BNGA', 'BNII', 'BNLI', 'BOBA', 'BOGA', 'BOLA', 'BOLT', 'BOSS', 'BPFI', 'BPTR', 'BRIS', 'BRMS', 'BRPT', 'BSDE', 'BSIM', 'BSML', 'BSSR', 'BTEK', 'BTON', 'BTPN', 'BTPS', 'BUDI', 'BUKA', 'BUKK', 'BULL', 'BUMI', 'BVIC', 'BWPT', 'BYAN', 'CAKK', 'CAMP', 'CANI', 'CARE', 'CARS', 'CASA', 'CASH', 'CASS', 'CBMF', 'CCSI', 'CEKA', 'CENT', 'CFIN', 'CINT', 'CITA', 'CITY', 'CLEO', 'CLPI', 'CMNP', 'CMNT', 'CMPP', 'CMRY', 'CNKO', 'CNTX', 'COCO', 'CPIN', 'CPRO', 'CSAP', 'CSIS', 'CSMI', 'CSRA', 'CTRA', 'DADA', 'DART', 'DAYA', 'DCII', 'DEAL', 'DEPO', 'DEWA', 'DFAM', 'DGIK', 'DGNS', 'DIGI', 'DILD', 'DIVA', 'DKFT', 'DLTA', 'DMAS', 'DMMX', 'DMND', 'DNAR', 'DNET', 'DOID', 'DPNS', 'DRMA', 'DSFI', 'DSNG', 'DUTI', 'DVLA', 'DWGL', 'DYAN', 'EAST', 'ECII', 'EDGE', 'EKAD', 'ELSA', 'ELTY', 'EMDE', 'EMTK', 'ENAK', 'ENRG', 'ENZO', 'EPAC', 'EPMT', 'ERAA', 'ERTX', 'ESIP', 'ESSA', 'ESTA', 'ESTI', 'EXCL', 'FAPA', 'FAST', 'FILM', 'FIMP', 'FIRE', 'FISH', 'FITT', 'FLMC', 'FMII', 'FOOD', 'FORU', 'FPNI', 'FREN', 'FUJI', 'GAMA', 'GDST', 'GDYR', 'GEMA', 'GEMS', 'GGRM', 'GGRP', 'GHON', 'GJTL', 'GLOB', 'GLVA', 'GMFI', 'GOLD', 'GOOD', 'GOTO', 'GPRA', 'GPSO', 'GSMF', 'GTSI', 'GWSA', 'GZCO', 'HAIS', 'HDFA', 'HDIT', 'HEAL', 'HELI', 'HERO', 'HEXA', 'HITS', 'HKMU', 'HMSP', 'HOKI', 'HOMI', 'HOPE', 'HRME', 'HRTA', 'HRUM', 'IATA', 'IBOS', 'IBST', 'ICBP', 'ICON', 'IDEA', 'IDPR', 'IFII', 'IFSH', 'IGAR', 'IKAN', 'IKBI', 'IMAS', 'IMJS', 'IMPC', 'INAF', 'INAI', 'INCF', 'INCI', 'INCO', 'INDF', 'INDO', 'INDR', 'INDS', 'INDX', 'INDY', 'INKP', 'INOV', 'INPC', 'INPP', 'INPS', 'INRU', 'INTD', 'INTP', 'IPAC', 'IPCC', 'IPCM', 'IPOL', 'IPPE', 'IPTV', 'IRRA', 'ISAT', 'ISSP', 'ITIC', 'ITMA', 'ITMG', 'JAST', 'JAWA', 'JAYA', 'JECC', 'JIHD', 'JKON', 'JMAS', 'JPFA', 'JRPT', 'JSKY', 'JSMR', 'JTPE', 'KAEF', 'KARW', 'KAYU', 'KBAG', 'KBLI', 'KBLM', 'KBLV', 'KDSI', 'KEEN', 'KEJU', 'KIAS', 'KICI', 'KIJA', 'KINO', 'KIOS', 'KJEN', 'KKGI', 'KLBF', 'KMDS', 'KMTR', 'KOBX', 'KOIN', 'KONI', 'KOPI', 'KOTA', 'KPIG', 'KRAS', 'KREN', 'KUAS', 'LABA', 'LAND', 'LCKM', 'LEAD', 'LFLO', 'LINK', 'LION', 'LMAS', 'LMPI', 'LMSH', 'LPCK', 'LPGI', 'LPIN', 'LPKR', 'LPLI', 'LPPF', 'LPPS', 'LSIP', 'LTLS', 'LUCK', 'LUCY', 'MAIN', 'MAPA', 'MAPI', 'MARI', 'MARK', 'MASA', 'MASB', 'MAYA', 'MBAP', 'MBSS', 'MBTO', 'MCAS', 'MCOL', 'MCOR', 'MDIA', 'MDKA', 'MDKI', 'MDLN', 'MEDC', 'MEGA', 'MERK', 'META', 'MFIN', 'MFMI', 'MGLV', 'MGRO', 'MICE', 'MIDI', 'MIKA', 'MIRA', 'MITI', 'MKNT', 'MKPI', 'MLBI', 'MLIA', 'MLPL', 'MLPT', 'MMLP', 'MNCN', 'MOLI', 'MPMX', 'MPOW', 'MPPA', 'MPRO', 'MRAT', 'MREI', 'MSIN', 'MSKY', 'MTDL', 'MTEL', 'MTLA', 'MTMH', 'MTPS', 'MTSM', 'MTWI', 'MYOH', 'MYOR', 'MYTX', 'NANO', 'NASA', 'NASI', 'NATO', 'NELY', 'NETV', 'NFCX', 'NICK', 'NICL', 'NIKL', 'NIRO', 'NISP', 'NOBU', 'NPGF', 'NRCA', 'NTBK', 'NZIA', 'OASA', 'OBMD', 'OILS', 'OKAS', 'OLIV', 'OMRE', 'OPMS', 'PADI', 'PALM', 'PAMG', 'PANI', 'PANR', 'PANS', 'PBID', 'PBRX', 'PBSA', 'PCAR', 'PDES', 'PEGE', 'PEHA', 'PGAS', 'PGJO', 'PGLI', 'PGUN', 'PICO', 'PJAA', 'PKPK', 'PLAN', 'PLIN', 'PMJS', 'PMMP', 'PNBN', 'PNBS', 'PNGO', 'PNIN', 'PNLF', 'POLA', 'POLI', 'POLL', 'POLU', 'POLY', 'POWR', 'PPGL', 'PPRE', 'PPRO', 'PRAS', 'PRDA', 'PRIM', 'PSAB', 'PSDN', 'PSGO', 'PSKT', 'PSSI', 'PTBA', 'PTDU', 'PTIS', 'PTPP', 'PTPW', 'PTRO', 'PTSN', 'PUDP', 'PURA', 'PURE', 'PURI', 'PWON', 'PYFA', 'PZZA', 'RAJA', 'RALS', 'RANC', 'RBMS', 'RDTX', 'REAL', 'RELI', 'RICY', 'RIGS', 'RISE', 'RMKE', 'ROCK', 'RODA', 'ROTI', 'RSGK', 'RUIS', 'RUNS', 'SAFE', 'SAME', 'SAMF', 'SAPX', 'SATU', 'SBAT', 'SBMA', 'SCCO', 'SCMA', 'SCNP', 'SDMU', 'SDPC', 'SDRA', 'SEMA', 'SFAN', 'SGER', 'SGRO', 'SHID', 'SHIP', 'SICO', 'SIDO', 'SILO', 'SIMP', 'SINI', 'SIPD', 'SKBM', 'SKLT', 'SKRN', 'SLIS', 'SMAR', 'SMBR', 'SMCB', 'SMDM', 'SMDR', 'SMGR', 'SMKL', 'SMKM', 'SMMT', 'SMRA', 'SMSM', 'SNLK', 'SOCI', 'SOFA', 'SOHO', 'SOSS', 'SOTS', 'SPMA', 'SPTO', 'SQMI', 'SRAJ', 'SRSN', 'SRTG', 'SSIA', 'SSMS', 'SSTM', 'STAA', 'STAR', 'STTP', 'SULI', 'SWAT', 'TALF', 'TAMA', 'TAPG', 'TAXI', 'TAYS', 'TBIG', 'TBLA', 'TBMS', 'TCID', 'TCPI', 'TEBE', 'TECH', 'TELE', 'TFAS', 'TGKA', 'TGRA', 'TIFA', 'TINS', 'TIRA', 'TIRT', 'TKIM', 'TLDN', 'TLKM', 'TMAS', 'TMPO', 'TNCA', 'TOBA', 'TOPS', 'TOTL', 'TOTO', 'TOWR', 'TOYS', 'TPIA', 'TPMA', 'TRIM', 'TRIN', 'TRIS', 'TRJA', 'TRST', 'TRUE', 'TRUK', 'TRUS', 'TSPC', 'TUGU', 'UANG', 'UCID', 'UFOE', 'ULTJ', 'UNIC', 'UNIQ', 'UNSP', 'UNTR', 'UNVR', 'URBN', 'UVCR', 'VICI', 'VICO', 'VINS', 'VIVA', 'VOKS', 'VRNA', 'WAPO', 'WEGE', 'WEHA', 'WGSH', 'WICO', 'WIFI', 'WIIM', 'WIKA', 'WINR', 'WINS', 'WIRG', 'WMPP', 'WMUU', 'WOMF', 'WOOD', 'WOWS', 'WSKT', 'WTON', 'YELO', 'YPAS', 'YULE', 'ZBRA', 'ZINC', 'ZONE', 'ZYRX']

class TradingViewScraper:
    def __init__(self,
                 target_url='https://www.tradingview.com/'):
                 
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

        self.target_url = target_url
        self.driver.get(self.target_url)

        # Create directory
        self.directory = f"./results/tradingview"
        create_directory(self.directory)
        self.directory_previous = f"./previous/tradingview"
        create_directory(self.directory_previous)

        # Get google drive API
        # Initialize google drive api
        self.gdrive_api = GoogleDriveAPI()

    def get_all_stock_code(
        self,
    ):
        # Define url
        url = f"https://www.tradingview.com/markets/stocks-indonesia/market-movers-all-stocks/"
        
        # Go to url
        self.driver.get(url)
        sleep(1)

        # Load all data
        while len(self.driver.find_elements(By.CLASS_NAME, 'loadButton-59hnCnPW')) != 0:
            load_more_click = self.driver.find_elements(By.CLASS_NAME, 'loadButton-59hnCnPW')[0]
            self.driver.execute_script("arguments[0].click();", load_more_click)
            sleep(1)
        
        # Create dataframe
        df = pd.read_html(self.driver.page_source)[1]
        
        # Get Stock Code and Company Name
        elements_stock_code = self.driver.find_elements(By.XPATH, '//*[@id="js-category-content"]/div/div/div[2]/div[2]/div/div[2]/div[2]/div/div/div/table/tbody/tr/td/span/a')
        elements_company_name = self.driver.find_elements(By.XPATH, '//*[@id="js-category-content"]/div/div/div[2]/div[2]/div/div[2]/div[2]/div/div/div/table/tbody/tr/td/span/sup')
        for i in range(0, len(df)):
            df.loc[i, "Stock Code"] = elements_stock_code[i].text
            df.loc[i, "Company Name"] = elements_company_name[i].text

        # Rename and reorder columns
        df = df.drop("Ticker", axis=1)
        rename_columns = {
            "Stock Code": "Stock Code",
            "Company Name": "Company Name",
            "Sector": "Sector",
            "Last": "Last",
            "Chg,\xa01D": "Change",
            "Chg %,\xa01D": "Change [%]",
            "Technical Rating,\xa01D": "Technical Rating",
            "Vol,\xa01D": "Vol",
            "Volume*price,\xa01D": "Volume*Price",
            "Mkt cap": "Market Cap",
            "P/E": "PE Ratio",
            "EPS (TTM)": "EPS (TTM)",
            "Employees": "Employees",
        }
        df = df.rename(columns=rename_columns)
        df = df[list(rename_columns.values())]

        # Clean dataframe
        # Remove IDR
        df["Last"] = df["Last"].apply(lambda x: x.replace('IDR', ''))
        df["Change"] = df["Change"].apply(lambda x: x.replace('IDR', ''))
        df["EPS (TTM)"] = df["EPS (TTM)"].apply(lambda x: x.replace('IDR', ''))
        df["Market Cap"] = df["Market Cap"].apply(lambda x: x.replace('IDR', ''))
        
        # Remove percentage
        df["Change [%]"] = df["Change [%]"].apply(lambda x: x.replace('%', ''))

        # Convert T, B, M, K
        df["Vol"] = df["Vol"].apply(lambda x: x.replace('T', '0000000000').replace('B', '0000000').replace('M', '0000').replace('K', '0').replace('.', ''))
        df["Volume*Price"] = df["Volume*Price"].apply(lambda x: x.replace('T', '0000000000').replace('B', '0000000').replace('M', '0000').replace('K', '0').replace('.', ''))
        df["Market Cap"] = df["Market Cap"].apply(lambda x: x.replace('T', '0000000000').replace('B', '0000000').replace('M', '0000').replace('K', '0').replace('.', ''))
        df["Employees"] = df["Employees"].apply(lambda x: x.replace('T', '0000000000').replace('B', '0000000').replace('M', '0000').replace('K', '0').replace('.', ''))
        
        # Save overview companies data as csv
        df.to_csv(f'{self.directory}/overview.csv')

        # Upload to google drive
        folder_id = os.environ["GDRIVE_FOLDER_ID_TRADINGVIEW"]

        # Concat with previous version
        try:
            query = f"name = 'overview.csv' and '{folder_id}' in parents"
            file_id = self.gdrive_api.file_list(query)[0].get("id")
            self.gdrive_api.file_update(f'{self.directory}/overview.csv', file_id)
        
        # Crete new file
        except:
            self.gdrive_api.file_upload(f'{self.directory}/overview.csv', folder_id)

    def get_fundamental_data(
        self,
        stock_filter: Optional[list] = None,
        year_filter: Optional[list] = None,
        period_filter: Optional[list] = None):

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

        # Define financial types
        financial_types = ["income-statement", "balance-sheet", "cash-flow", "statistics-and-ratios"]

        # Define period types
        period_types = ["yearly", "quarterly"]

        # Get stocks
        if stock_filter:
            stocks = stock_filter
        else:
            # Find overview file on google drive
            folder_id = os.environ["GDRIVE_FOLDER_ID_TRADINGVIEW"]
            query = f"name = 'overview.csv' and '{folder_id}' in parents"
            file_id = self.gdrive_api.file_list(query)[0].get("id")
            self.gdrive_api.file_download(file_id, f'{self.directory}/Overview.csv')

            overview = pd.read_csv(f'{self.directory}/Overview.csv', index_col=0)
            stocks = overview["Stock Code"].to_list()
        
        with alive_bar(len(stocks), force_tty=True) as bar:
            for stock in stocks:
                for period_type in period_types:
                    json_structure = {}
                    income_statement = pd.DataFrame()
                    balance_sheet = pd.DataFrame()
                    cash_flow = pd.DataFrame()
                    ratios = pd.DataFrame()

                    # Define folder id for uploading to google drive
                    if period_type == 'quarterly':
                        folder_id = os.environ["GDRIVE_FOLDER_ID_TRADINGVIEW_QUARTERLY"]
                    elif period_type == 'yearly':
                        folder_id = os.environ["GDRIVE_FOLDER_ID_TRADINGVIEW_YEARLY"]

                    for financial_type in financial_types: 
                        directory = f'{self.directory}/{period_type}'
                        create_directory(directory)

                        directory_previous = f'{self.directory_previous}/{period_type}'
                        create_directory(directory_previous)

                        # Define url
                        url = f"https://www.tradingview.com/symbols/IDX-{stock}/financials-{financial_type}/"
                        
                        try:
                            # Go to url
                            self.driver.get(url)

                            if period_type == 'yearly':                             
                                period_click = self.driver.find_elements(By.XPATH, '//*[@id="js-category-content"]/div/div[2]/div[2]/div/div/div[4]/div[2]/div/div/div/div/div/button')[0]
                                self.driver.execute_script("arguments[0].click();", period_click)
                            elif period_type == 'quarterly':
                                period_click = self.driver.find_elements(By.XPATH, '//*[@id="js-category-content"]/div/div[2]/div[2]/div/div/div[4]/div[2]/div/div/div/div/div/button')[1]
                                self.driver.execute_script("arguments[0].click();", period_click)

                            # Get all elements
                            sleep(1)
                            elements = self.driver.find_elements(By.XPATH, '//*[@id="js-category-content"]/div/div[2]/div[2]/div/div/div[5]/div[2]/div/div[1]/div')
                        except:
                            print(f"Cannot access fundamental data for stock: {stock}")
                            break
                        
                        # Define empty list for columns
                        columns = []

                        # Define double data every financial type
                        # Double data means that in the website, it has percentage for the differnce
                        # We will exclude those data since those data can be also determined post-scraping
                        doubles_income_statement = [
                            "Gross profit", 
                            "Total revenue",
                            "Operating income", 
                            "Pretax income", 
                            "Net income", 
                            "Basic earnings per share (Basic EPS)", 
                            "Diluted earnings per share (Diluted EPS)", 
                            "EBITDA", 
                            "EBIT",
                        ]
                        doubles_balance_sheet = [
                            "Total assets",
                            "Total liabilities",
                            "Total equity",
                        ]
                        doubles_cash_flow = [
                            "Cash from operating activities",
                            "Cash from investing activities",
                            "Cash from financing activities",
                            "Free cash flow",
                        ]
                        skip_ratios = [
                            "Valuation ratios",
                            "Key stats",
                            "Profitability ratios",
                            "Liquidity ratios",
                            "Solvency ratios",
                        ]

                        # Get all data from all elements
                        for element in elements:
                            text = element.text
                            data = pd.Series([x.replace("−","-") for x in text.replace('\n','#').replace('\u202c','#').replace('\u202a','#').replace('###','#').replace('##','#').split('#')])
                            if data[0] == "Currency: IDR":
                                # Define columns
                                for ix, row in data.items():
                                    if ix == 0:
                                        pass
                                    else:
                                        columns.append(row)
                            elif financial_type == 'income-statement':
                                for i in range (0, len(columns)):
                                    if data[0] in doubles_income_statement:
                                        try:
                                            if 't' in data[2*i+1].lower() or 'b' in data[2*i+1].lower() or 'm' in data[2*i+1].lower() or 'k' in data[2*i+1].lower():
                                                income_statement.loc[data[0], columns[i]] = float(data[2*i+1].replace('T', '0000000000').replace('B', '0000000').replace('M', '0000').replace('K', '0').replace('.',''))
                                            else:
                                                income_statement.loc[data[0], columns[i]] = float(data[2*i+1].replace('T', '0000000000').replace('B', '0000000').replace('M', '0000').replace('K', '0'))
                                        except:
                                            income_statement.loc[data[0], columns[i]] = data[2*i+1]
                                    else:
                                        try:
                                            if 't' in data[i+1].lower() or 'b' in data[i+1].lower() or 'm' in data[i+1].lower() or 'k' in data[i+1].lower():
                                                income_statement.loc[data[0], columns[i]] = float(data[i+1].replace('T', '0000000000').replace('B', '0000000').replace('M', '0000').replace('K', '0').replace('.',''))
                                            else:
                                                income_statement.loc[data[0], columns[i]] = float(data[i+1].replace('T', '0000000000').replace('B', '0000000').replace('M', '0000').replace('K', '0'))
                                        except:
                                            income_statement.loc[data[0], columns[i]] = data[i+1]
                            elif financial_type == 'balance-sheet':
                                for i in range (0, len(columns)):
                                    if data[0] in doubles_balance_sheet:
                                        try:
                                            if 't' in data[2*i+1].lower() or 'b' in data[2*i+1].lower() or 'm' in data[2*i+1].lower() or 'k' in data[2*i+1].lower():
                                                balance_sheet.loc[data[0], columns[i]] = float(data[2*i+1].replace('T', '0000000000').replace('B', '0000000').replace('M', '0000').replace('K', '0').replace('.',''))
                                            else:
                                                balance_sheet.loc[data[0], columns[i]] = float(data[2*i+1].replace('T', '0000000000').replace('B', '0000000').replace('M', '0000').replace('K', '0'))
                                        except:
                                            balance_sheet.loc[data[0], columns[i]] = data[2*i+1]
                                    else:
                                        try:
                                            if 't' in data[i+1].lower() or 'b' in data[i+1].lower() or 'm' in data[i+1].lower() or 'k' in data[i+1].lower():
                                                balance_sheet.loc[data[0], columns[i]] = float(data[i+1].replace('T', '0000000000').replace('B', '0000000').replace('M', '0000').replace('K', '0').replace('.',''))
                                            else:
                                                balance_sheet.loc[data[0], columns[i]] = float(data[i+1].replace('T', '0000000000').replace('B', '0000000').replace('M', '0000').replace('K', '0'))
                                        except:
                                            balance_sheet.loc[data[0], columns[i]] = data[i+1]
                            elif financial_type == 'cash-flow':
                                for i in range (0, len(columns)):
                                    if data[0] in doubles_cash_flow:
                                        try:
                                            if 't' in data[2*i+1].lower() or 'b' in data[2*i+1].lower() or 'm' in data[2*i+1].lower() or 'k' in data[2*i+1].lower():
                                                cash_flow.loc[data[0], columns[i]] = float(data[2*i+1].replace('T', '0000000000').replace('B', '0000000').replace('M', '0000').replace('K', '0').replace('.',''))
                                            else:
                                                cash_flow.loc[data[0], columns[i]] = float(data[2*i+1].replace('T', '0000000000').replace('B', '0000000').replace('M', '0000').replace('K', '0'))
                                        except:
                                            cash_flow.loc[data[0], columns[i]] = data[2*i+1]
                                    else:
                                        try:
                                            if 't' in data[i+1].lower() or 'b' in data[i+1].lower() or 'm' in data[i+1].lower() or 'k' in data[i+1].lower():
                                                cash_flow.loc[data[0], columns[i]] = float(data[i+1].replace('T', '0000000000').replace('B', '0000000').replace('M', '0000').replace('K', '0').replace('.',''))
                                            else:
                                                cash_flow.loc[data[0], columns[i]] = float(data[i+1].replace('T', '0000000000').replace('B', '0000000').replace('M', '0000').replace('K', '0'))
                                        except:
                                            cash_flow.loc[data[0], columns[i]] = data[i+1]
                            elif financial_type == 'statistics-and-ratios':
                                for i in range (0, len(columns)):
                                    if data[0] in skip_ratios:
                                        break
                                    else:
                                        try:
                                            if 't' in data[i+1].lower() or 'b' in data[i+1].lower() or 'm' in data[i+1].lower() or 'k' in data[i+1].lower():
                                                ratios.loc[data[0], columns[i]] = float(data[i+1].replace('T', '0000000000').replace('B', '0000000').replace('M', '0000').replace('K', '0').replace('.',''))
                                            else:
                                                ratios.loc[data[0], columns[i]] = float(data[i+1].replace('T', '0000000000').replace('B', '0000000').replace('M', '0000').replace('K', '0'))
                                        except:
                                            ratios.loc[data[0], columns[i]] = data[i+1]

                    # Structurized the json
                    if len(income_statement.columns) >= 1 and len(balance_sheet.columns) >= 1 and len(cash_flow.columns) >= 1 and len(ratios.columns) >= 1:
                        # Add to json structure
                        json_structure.update({"income_statement": json.loads(income_statement.to_json(orient='split', indent=4))})
                        json_structure.update({"balance_sheet": json.loads(balance_sheet.to_json(orient='split', indent=4))})
                        json_structure.update({"cash_flow": json.loads(cash_flow.to_json(orient='split', indent=4))})
                        json_structure.update({"ratios": json.loads(ratios.to_json(orient='split', indent=4))})

                        # Save the data in directory json
                        with open(f'{directory}/{stock}_{period_type}.json', 'w') as f:
                            f.write(json.dumps(json_structure, ensure_ascii=False, indent=4))

                        # Concat with previous version
                        try:
                            # Get file id
                            query = f"name = '{stock}_{period_type}.json' and '{folder_id}' in parents"
                            file_id = self.gdrive_api.file_list(query)[0].get("id")

                            # Download previous file
                            self.gdrive_api.file_download(file_id, f"{directory_previous}/{stock}_{period_type}.json")

                            with open(f"{directory_previous}/{stock}_{period_type}.json", 'rb') as f:
                                contents = f.read()
                                load_json = json.loads(contents.decode('ISO-8859-1'))
                                income_statement_previous = pd.DataFrame(load_json["income_statement"]["data"], index=load_json["income_statement"]["index"], columns=load_json["income_statement"]["columns"])
                                balance_sheet_previous = pd.DataFrame(load_json["balance_sheet"]["data"], index=load_json["balance_sheet"]["index"], columns=load_json["balance_sheet"]["columns"])
                                cash_flow_previous = pd.DataFrame(load_json["cash_flow"]["data"], index=load_json["cash_flow"]["index"], columns=load_json["cash_flow"]["columns"])

                            # Combine with previous data
                            income_statement = income_statement.combine_first(income_statement_previous)
                            balance_sheet = balance_sheet.combine_first(balance_sheet_previous)
                            cash_flow = cash_flow.combine_first(cash_flow_previous)

                            self.gdrive_api.file_update(f'{directory}/{stock}_{period_type}.json', file_id)

                        # Upload new file
                        except:
                            self.gdrive_api.file_upload(f'{directory}/{stock}_{period_type}.json', folder_id)

                    else:
                        print(f"No fundamental data available for stock: {stock}")

            bar()
        
        print(f"All fundamental data is downloaded and stored in: {self.directory} directory")

def create_directory(directory):
    # Check whether the specified path exists or not
    directory_exist = os.path.exists(directory)

    if not directory_exist:
        os.makedirs(directory, exist_ok = True)

def main():
    """Run fundamental analysis scraper"""
    tv_scraper = TradingViewScraper()

    # Get all stock code
    tv_scraper.get_all_stock_code()

    # Get fundamental data
    tv_scraper.get_fundamental_data()

if __name__ == '__main__':
    main()