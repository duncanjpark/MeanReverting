#!/usr/bin/env python3

from datetime import timedelta
import pandas as pd
from IPython.display import display
import matplotlib.pyplot as plt
import numpy as np
#from regex import F
from sklearn.decomposition import PCA
import statsmodels.api as sm

#Parameters
num_factors = 5
train_period_days = 252
num_quality_tickers = 10
#lookback = timedelta(days=60)
lookback = 5

"""
Separate Data Periods
"""
clean_table = pd.read_pickle(r'./Data.pkl')
#display(clean_table)

#Get Stock Returns and Cumulative Returns
stock_returns = (clean_table/clean_table.shift(1)-1).dropna()

#Separate return dataframes into training period and trading period
#train_returns = stock_returns[0:train_period_days]
trade_returns = stock_returns[train_period_days-lookback:]

"""
Training
"""

#Get top factors for each ticker using PCA

train_sample = clean_table[:train_period_days]
PCAmodel = PCA(num_factors)
PCAmodel.fit(train_sample)
factors = np.dot(train_sample, PCAmodel.components_.T)[:,:num_factors]
factors = sm.add_constant(factors)

#Train OLS Models for each ticker with their selected factors

OLSmodels = {ticker: sm.OLS(train_sample[ticker], factors).fit() for ticker in train_sample.columns}

#Get Reliability Score (mean-reversion speed)

#Get prediction values from OLS Models to create 1 day lagged data sets for each ticker
predictions = pd.DataFrame({ticker: OLSmodel.predict(factors) for ticker, OLSmodel in OLSmodels.items()})
predictions_lags = pd.DataFrame({ticker: np.roll(predictions[ticker], 1) for ticker in predictions})
predictions_lags.iloc[0] = 0
predictions_rets = predictions - predictions_lags
predictions_rets.iloc[0] = 0

#Create models for the returns vs lagged
return_models = {ticker: sm.OLS(predictions_rets[ticker], sm.add_constant(predictions_lags[ticker])).fit() for ticker in predictions_rets.columns}
half_lives = {ticker: np.log(0.5) / np.log(np.abs(return_model.params[1])) for ticker, return_model in return_models.items()}
#display(half_lives)

#Get highest scoring tickers
quality_tickers = dict(sorted(half_lives.items(), key=lambda x: x[1], reverse=False)[:num_quality_tickers])


"""
Portfolio Selection
"""
#trade_returns = trade_returns.filter(items=quality_tickers.keys())
trade_sample = clean_table[train_period_days-lookback:]
trade_sample = trade_sample.filter(items=quality_tickers.keys())
PCAmodel = PCA(num_factors)
PCAmodel.fit(trade_sample)
factors = np.dot(trade_sample, PCAmodel.components_.T)[:,:num_factors]
factors = sm.add_constant(factors)
#Iterate over days in trade_sample
display(trade_sample)
#for index in range(1, len(trade_sample.index)):
for index in range(1, 20):
    current_window = trade_sample.iloc[index:index + lookback]
    display(current_window)
    trading_models = {ticker: sm.OLS(current_window[ticker], factors[index:index + lookback]).fit() for ticker in current_window.columns}
    #predictions = pd.DataFrame({ticker: OLSmodel.predict(factors) for ticker, OLSmodel in OLSmodels.items()})
    R_squareds = {ticker: trading_model.rsquared for ticker, trading_model in trading_models.items()}
    display(R_squareds)


#Get Trading signals


#Select only quality trading signals based on R^2


"""
Trading
"""

#Dynamically adjust the portfolio by opening and closing the long/short positions


#plt.show()