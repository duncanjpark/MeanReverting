#!/usr/bin/env python3

import yfinance as yf
import pandas as pd
from IPython.display import display
import matplotlib.pyplot as plt
import numpy as np
from SPYholdings import main_etf
from yahooquery import Ticker
from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


period_length = '5y'
num_initial_tickers = 30

#Get Weightings of S&P500 Holdings
SPY_Holdings = main_etf('SPY')
#display(SPY_Holdings['Weight'])

#Get Data on tickers that are currently in SPY
tickers = Ticker(list(SPY_Holdings.index[:num_initial_tickers]), group_by='symbol', asynchronous=True, retry=20, status_forcelist=[404, 429, 500, 502, 503, 504])
#data = tickers.history(start='2018-01-01', end='2022-01-01')
data = tickers.history(period=period_length)
#display(data)

#Create Clean Table of Close Prices for tickers in Data
symbols = list(set(data.index.get_level_values(0)))
clean_table = data.loc['AAPL'][['close']]
clean_table.rename({'close': 'AAPL'}, axis=1, inplace=True)
for ticker in symbols:
    if ticker != 'AAPL':
        clean_table[ticker] = data.loc[ticker][['close']]
clean_table = clean_table.copy()
clean_table = clean_table.dropna(axis='columns')
symbols = clean_table.columns

#Write table to Excel file
clean_table.to_pickle(r'./Data.pkl')