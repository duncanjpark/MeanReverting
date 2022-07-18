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

SPY_Holdings = main_etf('SPY')
display(SPY_Holdings['Weight'])


tickers = Ticker(list(SPY_Holdings.index[:300]), group_by='symbol', asynchronous=True, retry=20, status_forcelist=[404, 429, 500, 502, 503, 504])
data = tickers.history(period='5y')
display(data)
symbols = list(set(data.index.get_level_values(0)))

clean_table = data.loc['AAPL'][['close']]
clean_table.rename({'close': 'AAPL'}, axis=1, inplace=True)
for ticker in symbols:
    if ticker != 'AAPL':
        clean_table[ticker] = data.loc[ticker][['close']]

clean_table = clean_table.copy()
display(clean_table)

stock_returns = (clean_table/clean_table.shift(1)-1).dropna()
cumul_returns = (1+stock_returns).cumprod()-1
display(cumul_returns)
#cumul_returns.iloc[:, :].plot()
corr_matrix = stock_returns.corr()
print(corr_matrix)

AAPL_factors = corr_matrix['AAPL']
print(AAPL_factors)

clean_table.to_csv(r'../Data.csv')

#plt.show()

