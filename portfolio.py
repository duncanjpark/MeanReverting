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

AAPL_changes = pd.DataFrame()
AAPL_price = pd.DataFrame()

purchase_max = 25000


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
        #spy_pos = 0
        #display(spy_pos)
        self.hedge_port(spy_pos, spy_price)
    
    def hedge_port(self, spy_pos, spy_price):
        pos_delta = spy_pos - self.hedge
        self.cash -= pos_delta * spy_price
        self.hedge = spy_pos
        self.hedge_val = self.hedge * spy_price
        spy_table.at[self.date, 'Position'] = spy_pos
        #return self.value

    def port_display(self):
        display(f'{self.date} : Portfolio Worth: { self.port_value( ) }')
    
    def port_holdings(self):
        for holding in self.port.values():
            holding.display()

    def port_value(self):
        self.total_value = self.cash + self.long_value + self.short_value + self.hedge_val
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
            self.init_short = self.value
            return self.value

        def open_long(self):
            if self.ticker == 'MSFT':
                AAPL_changes.at[self.date, 'Open Long'] = self.score
                AAPL_price.at[self.date, 'Open Long'] = self.price
            self.position = (math.floor(purchase_max / self.price))
            self.value = self.price * self.position
            return self.value

        def close_long(self):
            if self.ticker == 'MSFT':
                AAPL_changes.at[self.date, 'Close Long'] = self.score
                AAPL_price.at[self.date, 'Close Long'] = self.price
            self.value = self.position * self.price
            temp = self.value
            self.position = 0
            self.value = 0
            return temp
            

        def close_short(self):
            if self.ticker == 'MSFT':
                AAPL_changes.at[self.date, 'Close Short'] = self.score
                AAPL_price.at[self.date, 'Close Short'] = self.price
            self.value = self.position * self.price
            temp = self.value
            self.position = 0
            self.value = 0
            #display(f'Short Closed. Opened at {self.init_short}, closed at {temp}, meaning profit of {temp - self.init_short}')
            return temp
        
        def adjust(self, date, score):
            self.score = score
            self.date = date
            self.price = clean_table.at[self.date, self.ticker]
            self.change = 0
            if self.position == 0:
                if self.score > 1.5: #1.25:
                    self.change -= self.open_short()
                if self.score < -1.5: #-1.25:
                    self.change -= self.open_long()
            elif self.position < 0:
                if self.score < 0.75: #0.5:
                    self.change += self.close_short()
                else:
                    self.value = self.price * self.position
            else:
                if self.score > -0.5:
                    self.change += self.close_long()
                else:
                    self.value = self.price * self.position
            return self
        
        
