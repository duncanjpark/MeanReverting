#!/usr/bin/env python3

import yfinance as yf
import pandas as pd
from IPython.display import display
import matplotlib.pyplot as plt
import numpy as np
from SPYholdings import main_etf
from yahooquery import Ticker


SPY_Holdings = main_etf('SPY')
display(SPY_Holdings['Weight'])

# test
# test from mac

tickers = Ticker(list(SPY_Holdings.index[:20]), group_by='symbol', asynchronous=True, retry=20, status_forcelist=[404, 429, 500, 502, 503, 504])
data = tickers.history(period='2y')
display(data)
symbols = list(set(data.index.get_level_values(0)))
clean_table = data.loc['AAPL'][['close']]
clean_table.rename({'close': 'AAPL'}, axis=1, inplace=True)
for ticker in symbols:
    if ticker != 'AAPL':
        clean_table[ticker] = data.loc[ticker][['close']]
display(clean_table)

stock_returns = (clean_table/clean_table.shift(1)-1).dropna()
cumul_returns = (1+stock_returns).cumprod()-1
display(cumul_returns)
cumul_returns.iloc[:, :].plot()

tickers = Ticker(list(SPY_Holdings.index[240:260]), group_by='symbol', asynchronous=True, retry=20, status_forcelist=[404, 429, 500, 502, 503, 504])
data = tickers.history(period='2y')

symbols = list(set(data.index.get_level_values(0)))
clean_table = data.loc[symbols[0]][['close']]
clean_table.rename({'close': symbols[0]}, axis=1, inplace=True)
for ticker in symbols:
    if ticker != symbols[0]:
        clean_table[ticker] = data.loc[ticker][['close']]

stock_returns = (clean_table/clean_table.shift(1)-1).dropna()
cumul_returns = (1+stock_returns).cumprod()-1
display(cumul_returns)
cumul_returns.iloc[:, :].plot()

print(stock_returns.corr())

clean_table.to_csv(r'C:\Users\dunca\PycharmProjects\MeanReversion\Data.csv')
plt.show()

