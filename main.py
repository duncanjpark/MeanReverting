#!/usr/bin/env python3

#from datetime import timedelta
import pandas as pd
from IPython.display import display
import matplotlib.pyplot as plt
import numpy as np
#from regex import F
from sklearn.decomposition import PCA
import statsmodels.api as sm
from portfolio import AAPL_changes, AAPL_price
from portfolio import Portfolio

#Parameters
num_factors = 15
train_period_days = 252
num_quality_tickers = 75
#lookback = timedelta(days=60)
lookback = 30
R_squared_cutoff = 0.95
risk_free_rate = 0.02

"""
Separate Data Periods
"""
clean_table = pd.read_pickle(r'./Data.pkl')
spy_table = pd.read_pickle(r'./SPY.pkl')

#Get Stock Returns and Cumulative Returns
stock_returns = (clean_table/clean_table.shift(1)-1).dropna()

#Separate return dataframes into training period and trading period
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
#predictions = pd.DataFrame({ticker: OLSmodel.fittedvalues for ticker, OLSmodel in OLSmodels.items()})
predictions_lags = pd.DataFrame({ticker: np.roll(predictions[ticker], 1) for ticker in predictions})
predictions_lags.iloc[0] = 0
predictions_rets = predictions - predictions_lags
predictions_rets.iloc[0] = 0


#Create models for the returns vs lagged
return_models = {ticker: sm.OLS(predictions_rets[ticker], sm.add_constant(predictions_lags[ticker])).fit() for ticker in predictions_rets.columns}
half_lives = {ticker: np.log(0.5) / np.log(np.abs(return_model.params[1])) for ticker, return_model in return_models.items()}

#Get highest scoring tickers
quality_tickers = dict(sorted(half_lives.items(), key=lambda x: x[1], reverse=False)[:num_quality_tickers])

"""
Portfolio Selection
"""
trade_sample = clean_table[train_period_days-lookback:]
trade_sample = trade_sample.filter(items=quality_tickers.keys())
PCAmodel = PCA(num_factors)
PCAmodel = PCAmodel.fit(trade_sample)
factors = np.dot(trade_sample, PCAmodel.components_.T)[:,:num_factors]
factors = sm.add_constant(factors)

#Iterate over days in trade_sample

port = Portfolio()
port_value = {}
for index in range(lookback, len(trade_sample.index)):
#for index in range(lookback, 90 + lookback):
    #Select only quality tickers based on R^2
    current_window = trade_sample.iloc[index - lookback:index]
    trading_models = {ticker: sm.OLS(current_window[ticker], factors[index - lookback:index]).fit() for ticker in current_window.columns}
    R_squareds = {ticker: trading_model.rsquared for ticker, trading_model in trading_models.items()}
    R_squareds = dict(filter(lambda f: f[1] >= R_squared_cutoff, R_squareds.items()))
    ticks = R_squareds.keys()
    active_ticks = dict(filter(lambda f: f[1].position != 0, port.port.items())).keys()
    all_ticks = list(set(list(active_ticks) + list(ticks)))
    #if(len(missing_ticks) != 0):
    #    display(missing_ticks)
    #trading_models = dict(filter(lambda f: f[0] in R_squareds.keys(), trading_models.items()))
    trading_models = dict(filter(lambda f: f[0] in all_ticks, trading_models.items()))
    
    #Get Trading signals
    resids = pd.DataFrame({ticker: trading_model.resid for ticker, trading_model in trading_models.items()})
    zscores = ((resids - resids.mean()) / resids.std()).iloc[-1]

    """
    Trading
    """

    #Dynamically adjust the portfolio by opening and closing the long/short positions
    port.adjust_holdings(zscores)

    port.port_display()
    port_value[port.date] = port.total_value

port.port_holdings()
port_value = pd.DataFrame.from_dict(port_value, orient='index', columns=['Portfolio'])
log_return = np.sum(np.log(port_value/port_value.shift()), axis=1)
#log_return.plot()
sharpe_ratio = (log_return.mean() - risk_free_rate)/log_return.std()
asr = sharpe_ratio*252**.5

plt.figure(211)
with pd.plotting.plot_params.use("x_compat", True):
    AAPL_changes["Score"].plot(color="b")
    AAPL_changes["Open Short"].plot(marker="o", color='g')
    AAPL_changes["Open Long"].plot(marker="o", color='r')
    AAPL_changes["Close Short"].plot(marker="x", color='g')
    AAPL_changes["Close Long"].plot(marker="x", color='r')
    plt.legend()


plt.figure(212)
with pd.plotting.plot_params.use("x_compat", True):
    AAPL_price["Price"].plot(color="b")
    AAPL_price["Open Short"].plot(marker="o", color='g')
    AAPL_price["Open Long"].plot(marker="o", color='r')
    AAPL_price["Close Short"].plot(marker="x", color='g')
    AAPL_price["Close Long"].plot(marker="x", color='r')
    plt.legend()

#plt.figure(214)
port_value.plot()


plt.show()