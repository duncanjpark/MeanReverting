#!/usr/bin/env python3

import requests
import re
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  "Chrome/51.0.2704.103 Safari/537.36"
}


def main_etf(etf_key):
    url = ("https://www.zacks.com/funds/etf/" + etf_key + "/holding")
    with requests.Session() as req:
        req.headers.update(headers)
        r = req.get(url)
        etf_stock_list = re.findall(r'etf\\\/(.*?)\\', r.text)
        etf_stock_list = [x.replace('.', '-') for x in etf_stock_list]
        etf_stock_details_list = re.findall(
            r'<\\\/span><\\\/span><\\\/a>",(.*?), "<a class=\\\"report_[a-z]+ newwin\\', r.text)

        new_details = [x.replace('\"', '').replace(',', '').split() for x in etf_stock_details_list ]
        holdings = pd.DataFrame(new_details, index=etf_stock_list, columns=['Shares', 'Weight', '52 Wk Change(%)'])
        # display(holdings)
        return holdings




