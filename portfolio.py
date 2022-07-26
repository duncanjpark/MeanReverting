#!/usr/bin/env python3
#import backtrader as bt
from dis import dis
from IPython.display import display
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt


clean_table = pd.read_pickle(r'./Data.pkl')


#AAPL_changes = pd.DataFrame(clean_table.loc['2018-07-18':'2018-10-20','AAPL'])
#startdate = pd.to_datetime('2018-09-18').date()
#enddate = pd.to_datetime('2018-12-25').date()
#clean_table.loc[startdate:enddate, 'AAPL'].plot()
#AAPL_changes = pd.DataFrame(clean_table.loc[startdate:enddate,'AAPL'])
AAPL_changes = pd.DataFrame()
#AAPL_changes = pd.DataFrame(columns=['Price', 'Open Short', 'Close Short', 'Open Long', 'Close Long'])
#display(clean_table.loc[:,'AAPL'])

class Portfolio(object):
    def __init__(self) -> None:
        self.cash = 100000   # $100,000
        self.port = { }

    def adjust_holdings(self, scores):
        self.date = scores.name

        for ticker, score in scores.items():
            if ticker not in self.port.keys():
                self.port[ticker] = self.Holding(ticker, score)
            if ticker == 'AAPL':
                AAPL_changes.at[self.date, 'Score'] = score 
            self.port[ticker] = self.port[ticker].adjust(self.date, score)
            self.cash += self.port[ticker].change


    def port_display(self):
        display(f'{self.date} : Portfolio Worth: { self.port_value( ) }')
    
    def port_holdings(self):
        for holding in self.port.values():
            holding.display()

    def port_value(self):
        long_value = 0
        short_value = 0
        for holding in self.port.values():
            if holding.value > 0:
                long_value += holding.value
            else:
                short_value += holding.value
        self.total_value = self.cash + long_value + short_value
        return (f'Cash: {self.cash:6.2f} | Long Size: {long_value:6.2f} | Short Size: {short_value:6.2f}'
            f'| Total: {self.total_value:6.2f}')


    class Holding(object):
        def __init__(self, ticker, score) -> None:
            self.ticker = ticker
            self.score = score
            self.position = 0
            self.value = 0
            self.factor_collat = False  #does this holding have a position as a result of being a factor of a different ticker deviating from its mean?

        def display(self):
            display(self.ticker + " | " + str(self.position) + " | " + str(self.value))

        def open_short(self):
            if self.ticker == 'AAPL':
                AAPL_changes.at[self.date, 'Open Short'] = self.score
            self.position = -1
            self.value = self.price * self.position
            return self.value

        def open_long(self):
            if self.ticker == 'AAPL':
                AAPL_changes.at[self.date, 'Open Long'] = self.score
            self.position = 1
            self.value = self.price * self.position
            return self.value

        def close_long(self):
            if self.ticker == 'AAPL':
                AAPL_changes.at[self.date, 'Close Long'] = self.score
            temp = self.value
            self.position = 0
            self.value = 0
            return temp
            

        def close_short(self):
            if self.ticker == 'AAPL':
                AAPL_changes.at[self.date, 'Close Short'] = self.score
            temp = self.value
            self.position = 0
            self.value = 0
            return temp
        
        def adjust(self, date, score):
            self.score = score
            self.date = date
            self.price = clean_table.at[self.date, self.ticker]
            self.change = 0
            if self.position == 0:
                if self.score > 1.25:
                    self.change -= self.open_short()
                if self.score < -1.25:
                    self.change -= self.open_long()
            elif self.position < 0:
                if self.score < 0.5:
                    self.change += self.close_short()
                else:
                    self.value = self.price * self.position
            else:
                if self.score > -0.5:
                    self.change += self.close_long()
                else:
                    self.value = self.price * self.position
            return self
        
