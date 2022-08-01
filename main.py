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
#from portfolio import total_long_close_value, total_long_open_value, total_short_close_value, total_short_open_value, total_SPY_long_close_value, total_SPY_long_open_value, total_SPY_short_close_value, total_SPY_short_open_value
from portfolio import spy_table
#import pyfolio

#Parameters
num_factors = 10            # 15 > 5
train_period_days = 504     # 504 > 252 (seemingly) 
num_quality_tickers = 200   # 100 too volatile, 75 shit the bed for some reason... sticking with 50
lookback = 75               # trying 75
R_squared_cutoff = 0.965     #was .96, and it seems to be best for volatility and returns
risk_free_rate = 0.00       #

#10 factors, 504 train days, 90 lookback: 267 ending but not as good as 15, 503, 60 in beginning
#^seems less volatile

#10 factors, 504 days, 75 lookback seems to have more intra-month volatilaty but more consistent overall

#^ that same setup, but with 1.25/.5 score cutoffs worked great, goint to 291

#327 from 10, 504, 200, 75, .955, $10k max. seems it kinda just got lucky tho
"""
Separate Data Periods
"""
clean_table = pd.read_pickle(r'./Data.pkl')
#spy_table = pd.read_pickle(r'./SPY.pkl')

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
#for index in range(lookback, 252 + lookback):
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
"""
for ticker, score in zscores.items():
    if score < -.75 or score > .75:
        display(f'{ticker}: {score}')
"""
#port.port_holdings()

port_value = pd.DataFrame.from_dict(port_value, orient='index', columns=['Portfolio'])


#log_return = np.sum(np.log(port_value/port_value.shift()), axis=1)
#spy_log_return = np.sum(np.log(spy_table/spy_table.shift()), axis=1)
#spy_log_return.plot()

#log_return.plot()

#plt.figure(210)
log_return = np.sum(np.log(port_value/port_value.shift()), axis=1)
sharpe_ratio = (log_return.mean() - risk_free_rate)/log_return.std()
asr = sharpe_ratio*252**.5
print(f'Sharpe: {sharpe_ratio:.3f}, ASR: {asr:.3f}')


test = pd.DataFrame(spy_table['SPY'])
log_return = np.sum(np.log(test/test.shift()), axis=1)
sharpe_ratio = (log_return.mean() - risk_free_rate)/log_return.std()
asr = sharpe_ratio*252**.5
print(f'Sharpe: {sharpe_ratio:.3f}, ASR: {asr:.3f}')


"""
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
"""
plt.figure(214)

day1 = port_value.index[0]

#port_value['Daily Return'] = port_value['Portfolio'].pct_change(1)
#spy_table['Daily Return'] = spy_table['SPY'].pct_change(1)
#with pyfolio.plotting.plotting_context(font_scale=1.1):
#    pyfolio.create_full_tear_sheet(returns=port_value['Daily Return'], benchmark_rets=spy_table['Daily Return'], set_context=False)

spy_table = pd.DataFrame(spy_table)
spy_table.loc[:,'SPY'] = spy_table.loc[:,'SPY']  * ((100000) / spy_table.at[day1, 'SPY'])
#display(spy_table.head())
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