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


#Parameters
num_factors = 5
train_period_days = 252

"""
#Get Weightings of S&P500 Holdings
SPY_Holdings = main_etf('SPY')
#display(SPY_Holdings['Weight'])

#Get Data on tickers that are currently in SPY
tickers = Ticker(list(SPY_Holdings.index[:num_initial_tickers]), group_by='symbol', asynchronous=True, retry=20, status_forcelist=[404, 429, 500, 502, 503, 504])
#data = tickers.history(start='2018-01-01', end='2022-01-01')
data = tickers.history(period='3y')
display(data)

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
#display(clean_table)
"""

clean_table = pd.read_pickle(r'./Data.pkl')
display(clean_table)

#Get Stock Returns and Cumulative Returns
stock_returns = (clean_table/clean_table.shift(1)-1).dropna()
cumul_returns = (1+stock_returns).cumprod()-1
#display(cumul_returns)

#Separate return dataframes into training period and trading period
train_returns = stock_returns[0:train_period_days]
trade_returns = stock_returns[train_period_days:]


#Get Correlation Matrix of stock returns
corr_matrix = train_returns.corr(method='pearson')
print(corr_matrix)

#Get top factors for each ticker from correlation matrix
factors_dict = { }
for column in corr_matrix:
    factors_dict[column] = corr_matrix[column].sort_values(ascending=False)[1:num_factors + 1]
    display(factors_dict[column])
display(factors_dict)



#Show Plot
#plt.show()
