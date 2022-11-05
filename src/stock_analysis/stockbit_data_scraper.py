import json
import os
from time import sleep
from typing import Optional

import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient

IDX_30 = [
    "ADRO",
    "ANTM",
    "ASII",
    "BBCA",
    "BBNI",
    "BBRI",
    "BBTN",
    "BMRI",
    "BRPT",
    "BUKA",
    "CPIN",
    "EMTK",
    "EXCL",
    "ICBP",
    "INCO",
    "INDF",
    "INKP",
    "KLBF",
    "MDKA",
    "MIKA",
    "PGAS",
    "PTBA",
    "SMGR",
    "TBIG",
    "TINS",
    "TLKM",
    "TOWR",
    "UNTR",
    "UNVR",
    "WSKT",
]
LQ_45 = [
    "ADRO",
    "AMRT",
    "ANTM",
    "ASII",
    "BBCA",
    "BBNI",
    "BBRI",
    "BBTN",
    "BFIN",
    "BMRI",
    "BRPT",
    "BUKA",
    "CPIN",
    "EMTK",
    "ERAA",
    "EXCL",
    "GGRM",
    "HMSP",
    "HRUM",
    "ICBP",
    "INCO",
    "INDF",
    "INKP",
    "INTP",
    "ITMG",
    "JPFA",
    "KLBF",
    "MDKA",
    "MEDC",
    "MIKA",
    "MNCN",
    "PGAS",
    "PTBA",
    "PTPP",
    "SMGR",
    "TBIG",
    "TINS",
    "TKIM",
    "TLKM",
    "TOWR",
    "TPIA",
    "UNTR",
    "UNVR",
    "WIKA",
    "WSKT",
]
IDX_80 = [
    "AALI",
    "ACES",
    "ADRO",
    "AGII",
    "AKRA",
    "AMRT",
    "ANTM",
    "ASII",
    "ASRI",
    "ASSA",
    "BBCA",
    "BBNI",
    "BBRI",
    "BBTN",
    "BFIN",
    "BJBR",
    "BJTM",
    "BMRI",
    "BMTR",
    "BRPT",
    "BSDE",
    "BTPS",
    "BUKA",
    "CPIN",
    "CTRA",
    "DGNS",
    "DMAS",
    "DOID",
    "DSNG",
    "ELSA",
    "EMTK",
    "ERAA",
    "ESSA",
    "EXCL",
    "GGRM",
    "HEAL",
    "HMSP",
    "HOKI",
    "HRUM",
    "ICBP",
    "INCO",
    "INDF",
    "INKP",
    "INTP",
    "ISAT",
    "ITMG",
    "JPFA",
    "JSMR",
    "KAEF",
    "KLBF",
    "LPKR",
    "LPPF",
    "LSIP",
    "MAPI",
    "MDKA",
    "MEDC",
    "MIKA",
    "MNCN",
    "MYOR",
    "PGAS",
    "PTBA",
    "PTPP",
    "PWON",
    "SCMA",
    "SIDO",
    "SMGR",
    "SMRA",
    "SRTG",
    "TAPG",
    "TBIG",
    "TINS",
    "TKIM",
    "TLKM",
    "TOWR",
    "TPIA",
    "UNTR",
    "UNVR",
    "WIKA",
    "WMUU",
    "WSKT",
]
ALL = [
    "AALI",
    "ABBA",
    "ABDA",
    "ABMM",
    "ACES",
    "ACST",
    "ADES",
    "ADHI",
    "ADMF",
    "ADMG",
    "ADMR",
    "ADRO",
    "AGAR",
    "AGII",
    "AGRO",
    "AGRS",
    "AHAP",
    "AIMS",
    "AISA",
    "AKKU",
    "AKPI",
    "AKRA",
    "AKSI",
    "ALDO",
    "ALKA",
    "ALMI",
    "ALTO",
    "AMAG",
    "AMAN",
    "AMAR",
    "AMFG",
    "AMIN",
    "AMOR",
    "AMRT",
    "ANDI",
    "ANJT",
    "ANTM",
    "APEX",
    "APIC",
    "APII",
    "APLI",
    "APLN",
    "ARCI",
    "ARGO",
    "ARII",
    "ARKA",
    "ARMY",
    "ARNA",
    "ARTA",
    "ARTI",
    "ARTO",
    "ASBI",
    "ASDM",
    "ASGR",
    "ASII",
    "ASJT",
    "ASLC",
    "ASMI",
    "ASPI",
    "ASRI",
    "ASRM",
    "ASSA",
    "ATAP",
    "ATIC",
    "AUTO",
    "AVIA",
    "AYLS",
    "BABP",
    "BACA",
    "BAJA",
    "BALI",
    "BANK",
    "BAPA",
    "BAPI",
    "BATA",
    "BAUT",
    "BAYU",
    "BBCA",
    "BBHI",
    "BBKP",
    "BBLD",
    "BBMD",
    "BBNI",
    "BBRI",
    "BBRM",
    "BBSI",
    "BBSS",
    "BBTN",
    "BBYB",
    "BCAP",
    "BCIC",
    "BCIP",
    "BDMN",
    "BEBS",
    "BEEF",
    "BEKS",
    "BELL",
    "BESS",
    "BEST",
    "BFIN",
    "BGTG",
    "BHAT",
    "BHIT",
    "BIKA",
    "BIMA",
    "BINA",
    "BINO",
    "BIPI",
    "BIPP",
    "BIRD",
    "BISI",
    "BJBR",
    "BJTM",
    "BKDP",
    "BKSL",
    "BKSW",
    "BLTA",
    "BLTZ",
    "BLUE",
    "BMAS",
    "BMHS",
    "BMRI",
    "BMSR",
    "BMTR",
    "BNBA",
    "BNBR",
    "BNGA",
    "BNII",
    "BNLI",
    "BOBA",
    "BOGA",
    "BOLA",
    "BOLT",
    "BOSS",
    "BPFI",
    "BPII",
    "BPTR",
    "BRAM",
    "BRIS",
    "BRMS",
    "BRNA",
    "BRPT",
    "BSDE",
    "BSIM",
    "BSML",
    "BSSR",
    "BSWD",
    "BTEK",
    "BTEL",
    "BTON",
    "BTPN",
    "BTPS",
    "BUDI",
    "BUKA",
    "BUKK",
    "BULL",
    "BUMI",
    "BUVA",
    "BVIC",
    "BWPT",
    "BYAN",
    "CAKK",
    "CAMP",
    "CANI",
    "CARE",
    "CARS",
    "CASA",
    "CASH",
    "CASS",
    "CBMF",
    "CCSI",
    "CEKA",
    "CENT",
    "CFIN",
    "CINT",
    "CITA",
    "CITY",
    "CLAY",
    "CLEO",
    "CLPI",
    "CMNP",
    "CMNT",
    "CMPP",
    "CMRY",
    "CNKO",
    "CNTB",
    "CNTX",
    "COCO",
    "COWL",
    "CPIN",
    "CPRI",
    "CPRO",
    "CSAP",
    "CSIS",
    "CSMI",
    "CSRA",
    "CTBN",
    "CTRA",
    "CTTH",
    "DADA",
    "DART",
    "DAYA",
    "DCII",
    "DEAL",
    "DEFI",
    "DEPO",
    "DEWA",
    "DFAM",
    "DGIK",
    "DGNS",
    "DIGI",
    "DILD",
    "DIVA",
    "DKFT",
    "DLTA",
    "DMAS",
    "DMMX",
    "DMND",
    "DNAR",
    "DNET",
    "DOID",
    "DPNS",
    "DPUM",
    "DRMA",
    "DSFI",
    "DSNG",
    "DSSA",
    "DUCK",
    "DUTI",
    "DVLA",
    "DWGL",
    "DYAN",
    "EAST",
    "ECII",
    "EDGE",
    "EKAD",
    "ELSA",
    "ELTY",
    "EMDE",
    "EMTK",
    "ENAK",
    "ENRG",
    "ENVY",
    "ENZO",
    "EPAC",
    "EPMT",
    "ERAA",
    "ERTX",
    "ESIP",
    "ESSA",
    "ESTA",
    "ESTI",
    "ETWA",
    "EXCL",
    "FAPA",
    "FAST",
    "FASW",
    "FILM",
    "FIMP",
    "FIRE",
    "FISH",
    "FITT",
    "FLMC",
    "FMII",
    "FOOD",
    "FORU",
    "FORZ",
    "FPNI",
    "FREN",
    "FUJI",
    "GAMA",
    "GDST",
    "GDYR",
    "GEMA",
    "GEMS",
    "GGRM",
    "GGRP",
    "GHON",
    "GIAA",
    "GJTL",
    "GLOB",
    "GLVA",
    "GMFI",
    "GMTD",
    "GOLD",
    "GOLL",
    "GOOD",
    "GPRA",
    "GPSO",
    "GSMF",
    "GTBO",
    "GTSI",
    "GWSA",
    "GZCO",
    "HADE",
    "HAIS",
    "HDFA",
    "HDIT",
    "HDTX",
    "HEAL",
    "HELI",
    "HERO",
    "HEXA",
    "HITS",
    "HKMU",
    "HMSP",
    "HOKI",
    "HOME",
    "HOMI",
    "HOPE",
    "HOTL",
    "HRME",
    "HRTA",
    "HRUM",
    "IATA",
    "IBFN",
    "IBST",
    "ICBP",
    "ICON",
    "IDEA",
    "IDPR",
    "IFII",
    "IFSH",
    "IGAR",
    "IIKP",
    "IKAI",
    "IKAN",
    "IKBI",
    "IMAS",
    "IMJS",
    "IMPC",
    "INAF",
    "INAI",
    "INCF",
    "INCI",
    "INCO",
    "INDF",
    "INDO",
    "INDR",
    "INDS",
    "INDX",
    "INDY",
    "INKP",
    "INOV",
    "INPC",
    "INPP",
    "INPS",
    "INRU",
    "INTA",
    "INTD",
    "INTP",
    "IPAC",
    "IPCC",
    "IPCM",
    "IPOL",
    "IPPE",
    "IPTV",
    "IRRA",
    "ISAT",
    "ISSP",
    "ITIC",
    "ITMA",
    "ITMG",
    "JAST",
    "JAWA",
    "JAYA",
    "JECC",
    "JGLE",
    "JIHD",
    "JKON",
    "JKSW",
    "JMAS",
    "JPFA",
    "JRPT",
    "JSKY",
    "JSMR",
    "JSPT",
    "JTPE",
    "KAEF",
    "KARW",
    "KAYU",
    "KBAG",
    "KBLI",
    "KBLM",
    "KBLV",
    "KBRI",
    "KDSI",
    "KEEN",
    "KEJU",
    "KIAS",
    "KICI",
    "KIJA",
    "KINO",
    "KIOS",
    "KJEN",
    "KKGI",
    "KLBF",
    "KMDS",
    "KMTR",
    "KOBX",
    "KOIN",
    "KONI",
    "KOPI",
    "KOTA",
    "KPAL",
    "KPAS",
    "KPIG",
    "KRAH",
    "KRAS",
    "KREN",
    "KUAS",
    "LABA",
    "LAND",
    "LAPD",
    "LCGP",
    "LCKM",
    "LEAD",
    "LFLO",
    "LIFE",
    "LINK",
    "LION",
    "LMAS",
    "LMPI",
    "LMSH",
    "LPCK",
    "LPGI",
    "LPIN",
    "LPKR",
    "LPLI",
    "LPPF",
    "LPPS",
    "LRNA",
    "LSIP",
    "LTLS",
    "LUCK",
    "LUCY",
    "MABA",
    "MAGP",
    "MAIN",
    "MAMI",
    "MAMI",
    "MAPA",
    "MAPB",
    "MAPI",
    "MARI",
    "MARK",
    "MASA",
    "MASB",
    "MAYA",
    "MBAP",
    "MBSS",
    "MBTO",
    "MCAS",
    "MCOL",
    "MCOR",
    "MDIA",
    "MDKA",
    "MDKI",
    "MDLN",
    "MDRN",
    "MEDC",
    "MEGA",
    "MERK",
    "META",
    "MFIN",
    "MFMI",
    "MGLV",
    "MGNA",
    "MGRO",
    "MICE",
    "MIDI",
    "MIKA",
    "MINA",
    "MIRA",
    "MITI",
    "MKNT",
    "MKPI",
    "MLBI",
    "MLIA",
    "MLPL",
    "MLPT",
    "MMLP",
    "MNCN",
    "MOLI",
    "MPMX",
    "MPOW",
    "MPPA",
    "MPRO",
    "MRAT",
    "MREI",
    "MSIN",
    "MSKY",
    "MTDL",
    "MTEL",
    "MTFN",
    "MTLA",
    "MTPS",
    "MTRA",
    "MTSM",
    "MTWI",
    "MYOH",
    "MYOR",
    "MYRX",
    "MYRX",
    "MYTX",
    "NASA",
    "NASI",
    "NATO",
    "NELY",
    "NETV",
    "NFCX",
    "NICK",
    "NICL",
    "NIKL",
    "NIPS",
    "NIRO",
    "NISP",
    "NOBU",
    "NPGF",
    "NRCA",
    "NTBK",
    "NUSA",
    "NZIA",
    "OASA",
    "OBMD",
    "OCAP",
    "OILS",
    "OKAS",
    "OMRE",
    "OPMS",
    "PADI",
    "PALM",
    "PAMG",
    "PANI",
    "PANR",
    "PANS",
    "PBID",
    "PBRX",
    "PBSA",
    "PCAR",
    "PDES",
    "PEGE",
    "PEHA",
    "PGAS",
    "PGJO",
    "PGLI",
    "PGUN",
    "PICO",
    "PJAA",
    "PKPK",
    "PLAN",
    "PLAS",
    "PLIN",
    "PMJS",
    "PMMP",
    "PNBN",
    "PNBS",
    "PNGO",
    "PNIN",
    "PNLF",
    "PNSE",
    "POLA",
    "POLI",
    "POLL",
    "POLU",
    "POLY",
    "POOL",
    "PORT",
    "POSA",
    "POWR",
    "PPGL",
    "PPRE",
    "PPRO",
    "PRAS",
    "PRDA",
    "PRIM",
    "PSAB",
    "PSDN",
    "PSGO",
    "PSKT",
    "PSSI",
    "PTBA",
    "PTDU",
    "PTIS",
    "PTPP",
    "PTPW",
    "PTRO",
    "PTSN",
    "PTSP",
    "PUDP",
    "PURA",
    "PURE",
    "PURI",
    "PWON",
    "PYFA",
    "PZZA",
    "RAJA",
    "RALS",
    "RANC",
    "RBMS",
    "RDTX",
    "REAL",
    "RELI",
    "RICY",
    "RIGS",
    "RIMO",
    "RISE",
    "RMBA",
    "RMKE",
    "ROCK",
    "RODA",
    "RONY",
    "ROTI",
    "RSGK",
    "RUIS",
    "RUNS",
    "SAFE",
    "SAME",
    "SAMF",
    "SAPX",
    "SATU",
    "SBAT",
    "SBMA",
    "SCCO",
    "SCMA",
    "SCNP",
    "SCPI",
    "SDMU",
    "SDPC",
    "SDRA",
    "SEMA",
    "SFAN",
    "SGER",
    "SGRO",
    "SHID",
    "SHIP",
    "SIDO",
    "SILO",
    "SIMA",
    "SIMP",
    "SINI",
    "SIPD",
    "SKBM",
    "SKLT",
    "SKRN",
    "SKYB",
    "SLIS",
    "SMAR",
    "SMBR",
    "SMCB",
    "SMDM",
    "SMDR",
    "SMGR",
    "SMKL",
    "SMMA",
    "SMMT",
    "SMRA",
    "SMRU",
    "SMSM",
    "SNLK",
    "SOCI",
    "SOFA",
    "SOHO",
    "SONA",
    "SOSS",
    "SOTS",
    "SPMA",
    "SPTO",
    "SQMI",
    "SRAJ",
    "SRIL",
    "SRSN",
    "SRTG",
    "SSIA",
    "SSMS",
    "SSTM",
    "STAR",
    "STTP",
    "SUGI",
    "SULI",
    "SUPR",
    "SURE",
    "SWAT",
    "TALF",
    "TAMA",
    "TAMU",
    "TAPG",
    "TARA",
    "TAXI",
    "TAYS",
    "TBIG",
    "TBLA",
    "TBMS",
    "TCID",
    "TCPI",
    "TDPM",
    "TEBE",
    "TECH",
    "TELE",
    "TFAS",
    "TFCO",
    "TGKA",
    "TGRA",
    "TIFA",
    "TINS",
    "TIRA",
    "TIRT",
    "TKIM",
    "TLKM",
    "TMAS",
    "TMPO",
    "TNCA",
    "TOBA",
    "TOPS",
    "TOTL",
    "TOTO",
    "TOWR",
    "TOYS",
    "TPIA",
    "TPMA",
    "TRAM",
    "TRIL",
    "TRIM",
    "TRIN",
    "TRIO",
    "TRIS",
    "TRJA",
    "TRST",
    "TRUE",
    "TRUK",
    "TRUS",
    "TSPC",
    "TUGU",
    "TURI",
    "UANG",
    "UCID",
    "UFOE",
    "ULTJ",
    "UNIC",
    "UNIQ",
    "UNIT",
    "UNSP",
    "UNTR",
    "UNVR",
    "URBN",
    "UVCR",
    "VICI",
    "VICO",
    "VINS",
    "VIVA",
    "VOKS",
    "VRNA",
    "WAPO",
    "WEGE",
    "WEHA",
    "WGSH",
    "WICO",
    "WIFI",
    "WIIM",
    "WIKA",
    "WINS",
    "WMPP",
    "WMUU",
    "WOMF",
    "WOOD",
    "WOWS",
    "WSBP",
    "WSKT",
    "WTON",
    "YELO",
    "YPAS",
    "YULE",
    "ZBRA",
    "ZINC",
    "ZONE",
    "ZYRX",
]

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
        # chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), chrome_options=chrome_options
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
        statement_types = ["yearly", "quarterly"]

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

                json_structure_yearly = {"stock_code": f"{stock}"}
                json_structure_quarterly = {"stock_code": f"{stock}"}

                selection_report_type = Select(
                    self.driver.find_element(By.CLASS_NAME, "reportType")
                )
                selection_statement_type = Select(
                    self.driver.find_element(By.CLASS_NAME, "statement-type")
                )

                # Select always EN
                Select(
                    self.driver.find_element(By.CLASS_NAME, "transType")
                ).select_by_value("1")

                for report_type in report_types:
                    if report_type == "income-statement":
                        selection_report_type.select_by_value("1")
                    elif report_type == "balance-sheet":
                        selection_report_type.select_by_value("2")
                    elif report_type == "cash-flow":
                        selection_report_type.select_by_value("3")
                    sleep(2)

                    for statement_type in statement_types:
                        if statement_type == "quarterly":
                            selection_statement_type.select_by_value("1")
                        elif statement_type == "yearly":
                            selection_statement_type.select_by_value("2")
                        sleep(2)

                        # Always round to K
                        self.driver.find_element(
                            By.XPATH,
                            '//*[@id="content-box"]/div[3]/div[2]/div[1]/div[8]/div[3]/button[2]',
                        ).click()
                        self.driver.find_element(
                            By.XPATH,
                            '//*[@id="content-box"]/div[3]/div[2]/div[1]/div[8]/div[3]/button[2]',
                        ).click()
                        self.driver.find_element(
                            By.XPATH,
                            '//*[@id="content-box"]/div[3]/div[2]/div[1]/div[8]/div[3]/button[2]',
                        ).click()

                        tables = pd.read_html(self.driver.page_source)
                        df1 = tables[1].rename(columns={"In Thousand IDR": "In IDR", "In Billion IDR": "In IDR", "In Trillion IDR": "In IDR"})
                        df2 = tables[2].rename(columns={"In Thousand IDR": "In IDR", "In Billion IDR": "In IDR", "In Trillion IDR": "In IDR"})
                        data = pd.concat([df1, df2], axis=0)
                        data = data.fillna("")

                        data = data.set_index("In IDR")
                        data.columns = data.columns.str.replace("12M ", "")

                        for col in data.columns:
                            data[col] = data[col].apply(lambda x: str(x).replace(".", "").replace(" K", "0").replace(" B", "0000").replace(" T", "0000000").replace("-", "").replace(")", "").replace("(", "-")
                            if all(ext in x for ext in ([".","K"] or [".", "B"] or [".","T"])) else str(x).replace(",", "").replace(" K", "000").replace(" B", "000000").replace(" T", "000000000").replace("-", "").replace(")", "").replace("(", "-"))

                        if report_type == "income-statement":
                            data = data.rename(
                                index={
                                    "Net Income From Continuing Oper...": "Net Income From Continuing Operations",
                                    "Comprehensive Income Attributab...": "Comprehensive Income Attributabable To",
                                }
                            )
                            data = data[~data.index.duplicated(keep='first')]
                            if statement_type == "quarterly":
                                json_structure_quarterly.update(
                                    {
                                        "income_statement": json.loads(
                                            data.to_json()
                                        )
                                    }
                                )
                            elif statement_type == "yearly":
                                json_structure_yearly.update(
                                    {
                                        "income_statement": json.loads(
                                            data.to_json()
                                        )
                                    }
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
                            data = data[~data.index.duplicated(keep='first')]
                            if statement_type == "quarterly":
                                json_structure_quarterly.update(
                                    {
                                        "balance_sheet": json.loads(
                                            data.to_json()
                                        )
                                    }
                                )
                            elif statement_type == "yearly":
                                json_structure_yearly.update(
                                    {
                                        "balance_sheet": json.loads(
                                            data.to_json()
                                        )
                                    }
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
                            data = data[~data.index.duplicated(keep='first')]
                            if statement_type == "quarterly":
                                json_structure_quarterly.update(
                                    {
                                        "cash_flow": json.loads(
                                            data.to_json()
                                        )
                                    }
                                )
                            elif statement_type == "yearly":
                                json_structure_yearly.update(
                                    {
                                        "cash_flow": json.loads(
                                            data.to_json()
                                        )
                                    }
                                )

            except:
                print(f"Error in getting fundamental data available for stock: {stock}")

            # Store data to mongodb
            collection_yearly = self.db["yearly"]
            collection_quarterly = self.db["quarterly"]
            # Define filters based on domain_id
            filter = {"stock_code": f"{stock}"}

            # Determine values to be updated
            values_yearly = {"$set": json_structure_yearly}
            values_quarterly = {"$set": json_structure_quarterly}

            # Update values to database
            collection_yearly.update_one(filter=filter, update=values_yearly, upsert=True)
            collection_quarterly.update_one(filter=filter, update=values_quarterly, upsert=True)

        print(
            f"All fundamental data is downloaded and stored in the database"
        )


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

    # Get fundamental data
    stockbit_scraper.get_fundamental_data(stock_filter=ALL)


if __name__ == "__main__":
    main()
