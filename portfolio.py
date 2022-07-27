#!/usr/bin/env python3
#import backtrader as bt
from dis import dis
from IPython.display import display
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import math


clean_table = pd.read_pickle(r'./Data.pkl')
spy_table = pd.read_pickle(r'./SPY.pkl')


#AAPL_changes = pd.DataFrame(clean_table.loc['2018-07-18':'2018-10-20','AAPL'])
#startdate = pd.to_datetime('2018-09-18').date()
#enddate = pd.to_datetime('2018-12-25').date()
#clean_table.loc[startdate:enddate, 'AAPL'].plot()
#AAPL_changes = pd.DataFrame(clean_table.loc[startdate:enddate,'AAPL'])
AAPL_changes = pd.DataFrame()
AAPL_price = pd.DataFrame()
#AAPL_changes = pd.DataFrame(columns=['Price', 'Open Short', 'Close Short', 'Open Long', 'Close Long'])
#display(clean_table.loc[:,'AAPL'])
purchase_max = 1000

class Portfolio(object):
    def __init__(self) -> None:
        self.cash = 100000   # $100,000
        self.port = { }
        self.hedge = 0

    def adjust_holdings(self, scores):
        self.date = scores.name

        for ticker, score in scores.items():
            if ticker not in self.port.keys():
                self.port[ticker] = self.Holding(ticker, score)
            if ticker == 'MSFT':
                AAPL_changes.at[self.date, 'Score'] = score
                AAPL_price.at[self.date, 'Price'] = clean_table.at[self.date, ticker]
            self.port[ticker] = self.port[ticker].adjust(self.date, score)
            self.cash += self.port[ticker].change
        self.long_value = 0
        self.short_value = 0
        for holding in self.port.values():
            if holding.value > 0:
                self.long_value += holding.value
            else:
                self.short_value += holding.value
        spy_price = spy_table.at[self.date, 'SPY']
        spy_pos = -math.floor((self.long_value + self.short_value) / spy_price)
        #display(spy_pos)
        self.hedge_port(spy_pos, spy_price)
    
    def hedge_port(self, spy_pos, spy_price):
        pos_delta = self.hedge - spy_pos
        self.cash += pos_delta * spy_price
        self.hedge = spy_pos
        self.hedge_val = self.hedge * spy_price
        #return self.value

    def port_display(self):
        display(f'{self.date} : Portfolio Worth: { self.port_value( ) }')
    
    def port_holdings(self):
        for holding in self.port.values():
            holding.display()

    def port_value(self):
        self.total_value = self.cash + self.long_value + self.short_value
        return (f'Cash: {self.cash:9.2f} | Long Size: {self.long_value:9.2f} | Short Size: {self.short_value:9.2f}'
            f'| SPY Hedge: {self.hedge_val:9.2f} | Total: {self.total_value:9.2f}')


    class Holding(object):
        def __init__(self, ticker, score) -> None:
            self.ticker = ticker
            self.score = score
            self.position = 0
            self.value = 0
            #self.factor_collat = False  #does this holding have a position as a result of being a factor of a different ticker deviating from its mean?

        def display(self):
            display(self.ticker + " | " + str(self.position) + " | " + str(self.value))

        def open_short(self):
            if self.ticker == 'MSFT':
                AAPL_changes.at[self.date, 'Open Short'] = self.score
                AAPL_price.at[self.date, 'Open Short'] = self.price
            self.position = -(math.floor(purchase_max / self.price))
            self.value = self.price * self.position
            return self.value

        def open_long(self):
            if self.ticker == 'MSFT':
                AAPL_changes.at[self.date, 'Open Long'] = self.score
                AAPL_price.at[self.date, 'Open Long'] = self.price
            self.position = (math.floor(purchase_max / self.price))
            #display(f'Open long. {math.floor(purchase_max / self.price)}')

            self.value = self.price * self.position
            return self.value

        def close_long(self):
            if self.ticker == 'MSFT':
                AAPL_changes.at[self.date, 'Close Long'] = self.score
                AAPL_price.at[self.date, 'Close Long'] = self.price
            temp = self.value
            self.position = 0
            self.value = 0
            return temp
            

        def close_short(self):
            if self.ticker == 'MSFT':
                AAPL_changes.at[self.date, 'Close Short'] = self.score
                AAPL_price.at[self.date, 'Close Short'] = self.price
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
        
