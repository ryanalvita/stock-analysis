import os
import json

import numpy as np
import pandas as pd

from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from alive_progress import alive_bar

from typing import Optional

IDX_30 = ["ADRO","ANTM","ASII","BBCA","BBNI","BBRI","BBTN","BMRI","BRPT","BUKA","CPIN","EMTK","EXCL","ICBP","INCO","INDF","INKP","KLBF","MDKA","MIKA","PGAS","PTBA","SMGR","TBIG","TINS","TLKM","TOWR","UNTR","UNVR","WSKT"]
LQ_45 = ["ADRO","AMRT","ANTM","ASII","BBCA","BBNI","BBRI","BBTN","BFIN","BMRI","BRPT","BUKA","CPIN","EMTK","ERAA","EXCL","GGRM","HMSP","HRUM","ICBP","INCO","INDF","INKP","INTP","ITMG","JPFA","KLBF","MDKA","MEDC","MIKA","MNCN","PGAS","PTBA","PTPP","SMGR","TBIG","TINS","TKIM","TLKM","TOWR","TPIA","UNTR","UNVR","WIKA","WSKT"]
IDX_80 = ["AALI","ACES","ADRO","AGII","AKRA","AMRT","ANTM","ASII","ASRI","ASSA","BBCA","BBNI","BBRI","BBTN","BFIN","BJBR","BJTM","BMRI","BMTR","BRPT","BSDE","BTPS","BUKA","CPIN","CTRA","DGNS","DMAS","DOID","DSNG","ELSA","EMTK","ERAA","ESSA","EXCL","GGRM","HEAL","HMSP","HOKI","HRUM","ICBP","INCO","INDF","INKP","INTP","ISAT","ITMG","JPFA","JSMR","KAEF","KLBF","LPKR","LPPF","LSIP","MAPI","MDKA","MEDC","MIKA","MNCN","MYOR","PGAS","PTBA","PTPP","PWON","SCMA","SIDO","SMGR","SMRA","SRTG","TAPG","TBIG","TINS","TKIM","TLKM","TOWR","TPIA","UNTR","UNVR","WIKA","WMUU","WSKT"]

ALL = ["BVIC","BWPT","BYAN","CAKK","CAMP","CANI","CARE","CARS","CASA","CASH","CASS","CBMF","CCSI","CEKA","CENT","CFIN","CINT","CITA","CITY","CLAY","CLEO","CLPI","CMNP","CMNT","CMPP","CMRY","CNKO","CNTB","CNTX","COCO","COWL","CPIN","CPRI","CPRO","CSAP","CSIS","CSMI","CSRA","CTBN","CTRA","CTTH","DADA","DART","DAYA","DCII","DEAL","DEFI","DEPO","DEWA","DFAM","DGIK","DGNS","DIGI","DILD","DIVA","DKFT","DLTA","DMAS","DMMX","DMND","DNAR","DNET","DOID","DPNS","DPUM","DRMA","DSFI","DSNG","DSSA","DUCK","DUTI","DVLA","DWGL","DYAN","EAST","ECII","EDGE","EKAD","ELSA","ELTY","EMDE","EMTK","ENAK","ENRG","ENVY","ENZO","EPAC","EPMT","ERAA","ERTX","ESIP","ESSA","ESTA","ESTI","ETWA","EXCL","FAPA","FAST","FASW","FILM","FIMP","FIRE","FISH","FITT","FLMC","FMII","FOOD","FORU","FORZ","FPNI","FREN","FUJI","GAMA","GDST","GDYR","GEMA","GEMS","GGRM","GGRP","GHON","GIAA","GJTL","GLOB","GLVA","GMFI","GMTD","GOLD","GOLL","GOOD","GPRA","GPSO","GSMF","GTBO","GTSI","GWSA","GZCO","HADE","HAIS","HDFA","HDIT","HDTX","HEAL","HELI","HERO","HEXA","HITS","HKMU","HMSP","HOKI","HOME","HOMI","HOPE","HOTL","HRME","HRTA","HRUM","IATA","IBFN","IBST","ICBP","ICON","IDEA","IDPR","IFII","IFSH","IGAR","IIKP","IKAI","IKAN","IKBI","IMAS","IMJS","IMPC","INAF","INAI","INCF","INCI","INCO","INDF","INDO","INDR","INDS","INDX","INDY","INKP","INOV","INPC","INPP","INPS","INRU","INTA","INTD","INTP","IPAC","IPCC","IPCM","IPOL","IPPE","IPTV","IRRA","ISAT","ISSP","ITIC","ITMA","ITMG","JAST","JAWA","JAYA","JECC","JGLE","JIHD","JKON","JKSW","JMAS","JPFA","JRPT","JSKY","JSMR","JSPT","JTPE","KAEF","KARW","KAYU","KBAG","KBLI","KBLM","KBLV","KBRI","KDSI","KEEN","KEJU","KIAS","KICI","KIJA","KINO","KIOS","KJEN","KKGI","KLBF","KMDS","KMTR","KOBX","KOIN","KONI","KOPI","KOTA","KPAL","KPAS","KPIG","KRAH","KRAS","KREN","KUAS","LABA","LAND","LAPD","LCGP","LCKM","LEAD","LFLO","LIFE","LINK","LION","LMAS","LMPI","LMSH","LPCK","LPGI","LPIN","LPKR","LPLI","LPPF","LPPS","LRNA","LSIP","LTLS","LUCK","LUCY","MABA","MAGP","MAIN","MAMI","MAMI","MAPA","MAPB","MAPI","MARI","MARK","MASA","MASB","MAYA","MBAP","MBSS","MBTO","MCAS","MCOL","MCOR","MDIA","MDKA","MDKI","MDLN","MDRN","MEDC","MEGA","MERK","META","MFIN","MFMI","MGLV","MGNA","MGRO","MICE","MIDI","MIKA","MINA","MIRA","MITI","MKNT","MKPI","MLBI","MLIA","MLPL","MLPT","MMLP","MNCN","MOLI","MPMX","MPOW","MPPA","MPRO","MRAT","MREI","MSIN","MSKY","MTDL","MTEL","MTFN","MTLA","MTPS","MTRA","MTSM","MTWI","MYOH","MYOR","MYRX","MYRX","MYTX","NASA","NASI","NATO","NELY","NETV","NFCX","NICK","NICL","NIKL","NIPS","NIRO","NISP","NOBU","NPGF","NRCA","NTBK","NUSA","NZIA","OASA","OBMD","OCAP","OILS","OKAS","OMRE","OPMS","PADI","PALM","PAMG","PANI","PANR","PANS","PBID","PBRX","PBSA","PCAR","PDES","PEGE","PEHA","PGAS","PGJO","PGLI","PGUN","PICO","PJAA","PKPK","PLAN","PLAS","PLIN","PMJS","PMMP","PNBN","PNBS","PNGO","PNIN","PNLF","PNSE","POLA","POLI","POLL","POLU","POLY","POOL","PORT","POSA","POWR","PPGL","PPRE","PPRO","PRAS","PRDA","PRIM","PSAB","PSDN","PSGO","PSKT","PSSI","PTBA","PTDU","PTIS","PTPP","PTPW","PTRO","PTSN","PTSP","PUDP","PURA","PURE","PURI","PWON","PYFA","PZZA","RAJA","RALS","RANC","RBMS","RDTX","REAL","RELI","RICY","RIGS","RIMO","RISE","RMBA","RMKE","ROCK","RODA","RONY","ROTI","RSGK","RUIS","RUNS","SAFE","SAME","SAMF","SAPX","SATU","SBAT","SBMA","SCCO","SCMA","SCNP","SCPI","SDMU","SDPC","SDRA","SEMA","SFAN","SGER","SGRO","SHID","SHIP","SIDO","SILO","SIMA","SIMP","SINI","SIPD","SKBM","SKLT","SKRN","SKYB","SLIS","SMAR","SMBR","SMCB","SMDM","SMDR","SMGR","SMKL","SMMA","SMMT","SMRA","SMRU","SMSM","SNLK","SOCI","SOFA","SOHO","SONA","SOSS","SOTS","SPMA","SPTO","SQMI","SRAJ","SRIL","SRSN","SRTG","SSIA","SSMS","SSTM","STAR","STTP","SUGI","SULI","SUPR","SURE","SWAT","TALF","TAMA","TAMU","TAPG","TARA","TAXI","TAYS","TBIG","TBLA","TBMS","TCID","TCPI","TDPM","TEBE","TECH","TELE","TFAS","TFCO","TGKA","TGRA","TIFA","TINS","TIRA","TIRT","TKIM","TLKM","TMAS","TMPO","TNCA","TOBA","TOPS","TOTL","TOTO","TOWR","TOYS","TPIA","TPMA","TRAM","TRIL","TRIM","TRIN","TRIO","TRIS","TRJA","TRST","TRUE","TRUK","TRUS","TSPC","TUGU","TURI","UANG","UCID","UFOE","ULTJ","UNIC","UNIQ","UNIT","UNSP","UNTR","UNVR","URBN","UVCR","VICI","VICO","VINS","VIVA","VOKS","VRNA","WAPO","WEGE","WEHA","WGSH","WICO","WIFI","WIIM","WIKA","WINS","WMPP","WMUU","WOMF","WOOD","WOWS","WSBP","WSKT","WTON","YELO","YPAS","YULE","ZBRA","ZINC","ZONE","ZYRX"]

class TradingViewScraper:
    def __init__(self,
                 target_url='https://www.tradingview.com/'):
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

        self.target_url = target_url
        self.driver.get(self.target_url)

    def get_all_stock_code(
        self,
    ):
        # Define url
        url = f"https://www.tradingview.com/markets/stocks-indonesia/market-movers-all-stocks/"
        
        # Go to url
        self.driver.get(url)
        self.driver.maximize_window()
        sleep(2)

        # Load all data
        while len(self.driver.find_elements(By.CLASS_NAME, 'loadButton-59hnCnPW')) != 0:
            self.driver.find_elements(By.CLASS_NAME, 'loadButton-59hnCnPW')[0].click()
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
            "Chg": "Change",
            "Chg %": "Change [%]",
            "Technical Rating": "Technical Rating",
            "Vol": "Vol",
            "Volume*Price": "Volume*Price",
            "Mkt Cap": "Market Cap",
            "P/E": "PE Ratio",
            "EPS (TTM)": "EPS (TTM)",
            "EMPLOYEES": "Employees",
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
        df["Vol"] = df["Vol"].apply(lambda x: x.replace('T', '000000000000').replace('B', '000000000').replace('M', '000000').replace('K', '000').replace('.', ''))
        df["Volume*Price"] = df["Volume*Price"].apply(lambda x: x.replace('T', '000000000000').replace('B', '000000000').replace('M', '000000').replace('K', '000').replace('.', ''))
        df["Market Cap"] = df["Market Cap"].apply(lambda x: x.replace('T', '000000000000').replace('B', '000000000').replace('M', '000000').replace('K', '000').replace('.', ''))
        df["Employees"] = df["Employees"].apply(lambda x: x.replace('T', '000000000000').replace('B', '000000000').replace('M', '000000').replace('K', '000').replace('.', ''))
        
        # Create directory
        directory = f'./results'
        create_directory(directory)

        # Save overview companies data as csv
        df.to_csv(f'{directory}/Overview.csv')

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

        # Create directory
        directory = f'./results/'
        create_directory(directory)

        # Get stocks
        if stock_filter:
            stocks = stock_filter
        else:
            overview = pd.read_csv(f'{directory}/Overview.csv', index_col=0)
            stocks = overview["Stock Code"].to_list()
        
        with alive_bar(len(stocks), force_tty=True) as bar:
            for stock in stocks:
                json_structure = {}
                income_statement = pd.DataFrame()
                balance_sheet = pd.DataFrame()
                cash_flow = pd.DataFrame()
                ratios = pd.DataFrame()
                for financial_type in financial_types:
                    
                    # Define url
                    url = f"https://www.tradingview.com/symbols/IDX-{stock}/financials-{financial_type}/"
                    
                    try:
                        # Go to url
                        self.driver.get(url)
                        sleep(1)

                        # Get all elements
                        elements = self.driver.find_elements(By.XPATH, '//*[@id="js-category-content"]/div/div[2]/div[2]/div[2]/div/div[3]/div[2]/div/div')
                        sleep(1)
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
                                            income_statement.loc[data[0], columns[i]] = float(data[2*i+1].replace('T', '000000000000').replace('B', '000000000').replace('M', '000000').replace('K', '000').replace('.',''))
                                        else:
                                            income_statement.loc[data[0], columns[i]] = float(data[2*i+1].replace('T', '000000000000').replace('B', '000000000').replace('M', '000000').replace('K', '000'))
                                    except:
                                        income_statement.loc[data[0], columns[i]] = data[2*i+1]
                                else:
                                    try:
                                        if 't' in data[i+1].lower() or 'b' in data[i+1].lower() or 'm' in data[i+1].lower() or 'k' in data[i+1].lower():
                                            income_statement.loc[data[0], columns[i]] = float(data[i+1].replace('T', '000000000000').replace('B', '000000000').replace('M', '000000').replace('K', '000').replace('.',''))
                                        else:
                                            income_statement.loc[data[0], columns[i]] = float(data[i+1].replace('T', '000000000000').replace('B', '000000000').replace('M', '000000').replace('K', '000'))
                                    except:
                                        income_statement.loc[data[0], columns[i]] = data[i+1]
                        elif financial_type == 'balance-sheet':
                            for i in range (0, len(columns)):
                                if data[0] in doubles_balance_sheet:
                                    try:
                                        if 't' in data[2*i+1].lower() or 'b' in data[2*i+1].lower() or 'm' in data[2*i+1].lower() or 'k' in data[2*i+1].lower():
                                            balance_sheet.loc[data[0], columns[i]] = float(data[2*i+1].replace('T', '000000000000').replace('B', '000000000').replace('M', '000000').replace('K', '000').replace('.',''))
                                        else:
                                            balance_sheet.loc[data[0], columns[i]] = float(data[2*i+1].replace('T', '000000000000').replace('B', '000000000').replace('M', '000000').replace('K', '000'))
                                    except:
                                        balance_sheet.loc[data[0], columns[i]] = data[2*i+1]
                                else:
                                    try:
                                        if 't' in data[i+1].lower() or 'b' in data[i+1].lower() or 'm' in data[i+1].lower() or 'k' in data[i+1].lower():
                                            balance_sheet.loc[data[0], columns[i]] = float(data[i+1].replace('T', '000000000000').replace('B', '000000000').replace('M', '000000').replace('K', '000').replace('.',''))
                                        else:
                                            balance_sheet.loc[data[0], columns[i]] = float(data[i+1].replace('T', '000000000000').replace('B', '000000000').replace('M', '000000').replace('K', '000'))
                                    except:
                                        balance_sheet.loc[data[0], columns[i]] = data[i+1]
                        elif financial_type == 'cash-flow':
                            for i in range (0, len(columns)):
                                if data[0] in doubles_cash_flow:
                                    try:
                                        if 't' in data[2*i+1].lower() or 'b' in data[2*i+1].lower() or 'm' in data[2*i+1].lower() or 'k' in data[2*i+1].lower():
                                            cash_flow.loc[data[0], columns[i]] = float(data[2*i+1].replace('T', '000000000000').replace('B', '000000000').replace('M', '000000').replace('K', '000').replace('.',''))
                                        else:
                                            cash_flow.loc[data[0], columns[i]] = float(data[2*i+1].replace('T', '000000000000').replace('B', '000000000').replace('M', '000000').replace('K', '000'))
                                    except:
                                        cash_flow.loc[data[0], columns[i]] = data[2*i+1]
                                else:
                                    try:
                                        if 't' in data[i+1].lower() or 'b' in data[i+1].lower() or 'm' in data[i+1].lower() or 'k' in data[i+1].lower():
                                            cash_flow.loc[data[0], columns[i]] = float(data[i+1].replace('T', '000000000000').replace('B', '000000000').replace('M', '000000').replace('K', '000').replace('.',''))
                                        else:
                                            cash_flow.loc[data[0], columns[i]] = float(data[i+1].replace('T', '000000000000').replace('B', '000000000').replace('M', '000000').replace('K', '000'))
                                    except:
                                        cash_flow.loc[data[0], columns[i]] = data[i+1]
                        elif financial_type == 'statistics-and-ratios':
                            for i in range (0, len(columns)):
                                if data[0] in skip_ratios:
                                    break
                                else:
                                    try:
                                        if 't' in data[i+1].lower() or 'b' in data[i+1].lower() or 'm' in data[i+1].lower() or 'k' in data[i+1].lower():
                                            ratios.loc[data[0], columns[i]] = float(data[i+1].replace('T', '000000000000').replace('B', '000000000').replace('M', '000000').replace('K', '000').replace('.',''))
                                        else:
                                            ratios.loc[data[0], columns[i]] = float(data[i+1].replace('T', '000000000000').replace('B', '000000000').replace('M', '000000').replace('K', '000'))
                                    except:
                                        ratios.loc[data[0], columns[i]] = data[i+1]

                # Structurized the json
                if len(income_statement.columns) >= 1 and len(balance_sheet.columns) >= 1 and len(cash_flow.columns) >= 1 and len(ratios.columns) >= 1:
                    json_structure.update({"income_statement": json.loads(income_statement.to_json(orient='split', indent=4))})
                    json_structure.update({"balance_sheet": json.loads(balance_sheet.to_json(orient='split', indent=4))})
                    json_structure.update({"cash_flow": json.loads(cash_flow.to_json(orient='split', indent=4))})
                    json_structure.update({"ratios": json.loads(ratios.to_json(orient='split', indent=4))})

                    # Save the data in json
                    with open(f'{directory}/{stock}.json', 'w') as f:
                        f.write(json.dumps(json_structure, ensure_ascii=False, indent=4))
                else:
                    print(f"No fundamental data available for stock: {stock}")

                bar()
        
        print(f"All fundamental data is downloaded and stored in: {directory} directory")

def create_directory(directory):
    # Check whether the specified path exists or not
    directory_exist = os.path.exists(directory)

    if not directory_exist:
        os.makedirs(directory, exist_ok = True)

def main():
    """Run fundamental analysis scraper"""
    tv_scraper = TradingViewScraper()

    # Get all companies data
    tv_scraper.get_all_stock_code()

    # Get fundamental data
    tv_scraper.get_fundamental_data()

if __name__ == '__main__':
    main()