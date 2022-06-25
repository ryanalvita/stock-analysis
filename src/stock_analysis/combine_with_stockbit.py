import json
from importlib.metadata import files
from os import walk

import pandas as pd

file_list = []
for (dirpaths, dirnames, filenames) in walk ('./results/tradingview/quarterly'):
    file_list.extend([filename[0:4] for filename in filenames])

for stock_code in file_list:
    with open(f'results/tradingview/yearly/{stock_code}.json', 'rb') as f:
        contents = f.read()
        load_json = json.loads(contents.decode('ISO-8859-1'))
        income_statement_tv = pd.DataFrame(load_json["income_statement"]["data"], index=load_json["income_statement"]["index"], columns=load_json["income_statement"]["columns"])
        balance_sheet_tv = pd.DataFrame(load_json["balance_sheet"]["data"], index=load_json["balance_sheet"]["index"], columns=load_json["balance_sheet"]["columns"])
        cash_flow_tv = pd.DataFrame(load_json["cash_flow"]["data"], index=load_json["cash_flow"]["index"], columns=load_json["cash_flow"]["columns"])
        ratios_tv = pd.DataFrame(load_json["ratios"]["data"], index=load_json["ratios"]["index"], columns=load_json["ratios"]["columns"])

    with open(f'results/stockbit/yearly/{stock_code}.json', 'rb') as f:
        contents = f.read()
        load_json = json.loads(contents.decode('ISO-8859-1'))
        income_statement_sb = pd.DataFrame(load_json["income_statement"]["data"], index=load_json["income_statement"]["index"], columns=load_json["income_statement"]["columns"])
        balance_sheet_sb = pd.DataFrame(load_json["balance_sheet"]["data"], index=load_json["balance_sheet"]["index"], columns=load_json["balance_sheet"]["columns"])
        cash_flow_sb = pd.DataFrame(load_json["cash_flow"]["data"], index=load_json["cash_flow"]["index"], columns=load_json["cash_flow"]["columns"])

        income_statement_tv = income_statement_tv[income_statement_tv.columns[::-1]]
        balance_sheet_tv = balance_sheet_tv[balance_sheet_tv.columns[::-1]]
        cash_flow_tv = cash_flow_tv[cash_flow_tv.columns[::-1]]
        ratios_tv = ratios_tv[ratios_tv.columns[::-1]]

        json_structure = {}
        if len(income_statement_tv.columns) >= 1 and len(balance_sheet_tv.columns) >= 1 and len(cash_flow_tv.columns) >= 1 and len(ratios_tv.columns) >= 1:
            json_structure.update({"income_statement": json.loads(income_statement_tv.to_json(orient='split', indent=4))})
            json_structure.update({"balance_sheet": json.loads(balance_sheet_tv.to_json(orient='split', indent=4))})
            json_structure.update({"cash_flow": json.loads(cash_flow_tv.to_json(orient='split', indent=4))})
            json_structure.update({"ratios": json.loads(ratios_tv.to_json(orient='split', indent=4))})

            # Save the data in json
            with open(f'results/tradingview/quarterly/test/{stock_code}.json', 'w') as f:
                f.write(json.dumps(json_structure, ensure_ascii=False, indent=4))
    # with open(f'results/stockbit/quarterly/{stock_code}.json', 'rb') as f:
    #     contents = f.read()
    #     load_json = json.loads(contents.decode('ISO-8859-1'))
    #     income_statement_sb = pd.DataFrame(load_json["income_statement"]["data"], index=load_json["income_statement"]["index"], columns=load_json["income_statement"]["columns"])
    #     balance_sheet_sb = pd.DataFrame(load_json["balance_sheet"]["data"], index=load_json["balance_sheet"]["index"], columns=load_json["balance_sheet"]["columns"])
    #     cash_flow_sb = pd.DataFrame(load_json["cash_flow"]["data"], index=load_json["cash_flow"]["index"], columns=load_json["cash_flow"]["columns"])
    a=1

a=1


