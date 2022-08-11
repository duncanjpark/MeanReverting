#!/usr/bin/env python3

import pandas as pd
from yahooquery import Ticker
from warnings import simplefilter
import requests
import re
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

#Parameters
period_length = '10y'
num_initial_tickers = 500
etf_key = 'SPY'
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  "Chrome/51.0.2704.103 Safari/537.36"
}

url = ("https://www.zacks.com/funds/etf/" + etf_key + "/holding")
with requests.Session() as req:
    req.headers.update(headers)
    r = req.get(url)
    etf_stock_list = re.findall(r'etf\\\/(.*?)\\', r.text)
    etf_stock_list = [x.replace('.', '-') for x in etf_stock_list]
    etf_stock_details_list = re.findall(
        r'<\\\/span><\\\/span><\\\/a>",(.*?), "<a class=\\\"report_[a-z]+ newwin\\', r.text)

    new_details = [x.replace('\"', '').replace(',', '').split() for x in etf_stock_details_list ]
    holdings = pd.DataFrame(new_details[:num_initial_tickers], index=etf_stock_list[:num_initial_tickers], columns=['Shares', 'Weight', '52 Wk Change(%)'])

#Get Data on tickers that are currently in SPY
tickers = Ticker(list(holdings.index[:num_initial_tickers]), group_by='symbol', asynchronous=True, retry=20, status_forcelist=[404, 429, 500, 502, 503, 504])
data = tickers.history(period=period_length)
spy_ticker = Ticker(['SPY', 'INDU'], group_by='symbol', asynchronous=True, retry=20, status_forcelist=[404, 429, 500, 502, 503, 504])
spy_data = spy_ticker.history(period=period_length)

#Create Clean Table of Close Prices for tickers in Data
symbols = list(set(data.index.get_level_values(0)))
clean_table = data.loc['AAPL'][['close']]
temp = clean_table
clean_table.rename({'close': 'AAPL'}, axis=1, inplace=True)
for ticker in symbols:
    if ticker != 'AAPL':
        clean_table[ticker] = data.loc[ticker][['close']]
clean_table = clean_table.copy()
clean_table = clean_table.dropna(axis='columns')
symbols = clean_table.columns

#Create clean SPY Table
symbols = list(set(spy_data.index.get_level_values(0)))
spy_table = spy_data.loc['SPY'][['close']]
spy_table.rename({'close': 'SPY'}, axis=1, inplace=True)
for ticker in symbols:
    if ticker != 'SPY':
        spy_table[ticker] = spy_data.loc[ticker][['close']]
spy_table = spy_table.copy()
spy_table = spy_table.dropna(axis='columns')
symbols = spy_table.columns

#Write table to pkl file
clean_table.to_pickle(r'./Data.pkl')
spy_table.to_pickle(r'./SPY.pkl')