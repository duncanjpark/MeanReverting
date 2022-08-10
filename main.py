#!/usr/bin/env python3


import pandas as pd
from IPython.display import display
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
import statsmodels.api as sm
from portfolio import AAPL_changes, AAPL_price
from portfolio import Portfolio
from portfolio import spy_table

#Parameters
num_factors = 10            
train_period_days = 504      
num_quality_tickers = 200   
lookback = 75               
R_squared_cutoff = 0.965 
risk_free_rate = 0.00 


"""
Separate Data Periods
"""
clean_table = pd.read_pickle(r'./Data.pkl')

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

#Train PCA model using quality tickers only
PCAmodel = PCA(num_factors)
PCAmodel = PCAmodel.fit(trade_sample)
factors = np.dot(trade_sample, PCAmodel.components_.T)[:,:num_factors]
factors = sm.add_constant(factors)

#Iterate over days in trade_sample

port = Portfolio()  #Just for tracking some data points
port_value = {}

for index in range(lookback, len(trade_sample.index)):
    #Select only quality tickers based on R^2
    current_window = trade_sample.iloc[index - lookback:index]
    trading_models = {ticker: sm.OLS(current_window[ticker], factors[index - lookback:index]).fit() for ticker in current_window.columns}
    
    #Get R^2s for each ticker
    R_squareds = {ticker: trading_model.rsquared for ticker, trading_model in trading_models.items()}
    R_squareds = dict(filter(lambda f: f[1] >= R_squared_cutoff, R_squareds.items()))
    
    #Make sure to include tickers with open positions, even if they don't pass R^2 screening
    active_ticks = dict(filter(lambda f: f[1].position != 0, port.port.items())).keys()
    all_ticks = list(set(list(active_ticks) + list(R_squareds.keys())))

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

port_value = pd.DataFrame.from_dict(port_value, orient='index', columns=['Portfolio'])


#Calculating Annualized Sharpe Ratio
log_return = np.sum(np.log(port_value/port_value.shift()), axis=1)
sharpe_ratio = (log_return.mean() - risk_free_rate)/log_return.std()
asr = sharpe_ratio*252**.5
print(f'Sharpe: {sharpe_ratio:.3f}, ASR: {asr:.3f}')

#Benchmark
test = pd.DataFrame(spy_table['SPY'])
log_return = np.sum(np.log(test/test.shift()), axis=1)
sharpe_ratio = (log_return.mean() - risk_free_rate)/log_return.std()
asr = sharpe_ratio*252**.5
print(f'Sharpe: {sharpe_ratio:.3f}, ASR: {asr:.3f}')

#Demonstrating trading strategy via plots
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

plt.figure(214)

day1 = port_value.index[0]


spy_table = pd.DataFrame(spy_table)
spy_table.loc[:,'SPY'] = spy_table.loc[:,'SPY']  * ((100000) / spy_table.at[day1, 'SPY'])
spy_table = pd.DataFrame(spy_table.loc[day1:])
with pd.plotting.plot_params.use("x_compat", True):
    spy_table['SPY'].plot()
    port_value['Portfolio'].plot()

plt.figure(215)
#spy_pos_ewm = spy_table['Position'].ewm(span=10).mean()
#spy_pos_ewm.plot()

spy_lev = spy_table['Leverage'].ewm(span=30).mean()
spy_lev.plot()
#spy_scores = (spy_table['Scores'].ewm(span=5).mean()) / 8
#spy_scores.plot()
#spy_count = spy_table['Count'].ewm(span=30).mean()
#spy_count.plot()

plt.show()
