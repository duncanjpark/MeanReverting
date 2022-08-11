#!/usr/bin/env python3
from dis import dis
from IPython.display import display
import pandas as pd
import math
import numpy as np

clean_table = pd.read_pickle(r'./Data.pkl')
spy_table = pd.read_pickle(r'./SPY.pkl')

AAPL_changes = pd.DataFrame()
AAPL_price = pd.DataFrame()


class Portfolio(object):
    def __init__(self) -> None:
        self.cash = 100000   # $100,000
        self.port = { }      # dictionary of holdings
        self.hedge = 0


    def adjust_holdings(self, scores):
        #update date
        self.date = scores.name
        spy_table.at[self.date, 'Scores'] = len(scores.index)

        
        #Adjust the maximum purchase amount for each holding for trading due by estimating number of tickers with viable signals (in order to control leverage) 
        temp_count = 0
        for ticker, score in scores.items():
            if score > 1.5 or score < -1.5:
                temp_count += 1
        self.max_purchase = min(self.cash * (.115), max((.138 * self.cash) - (.01 * self.cash * temp_count), self.cash * .028))

        for ticker, score in scores.items():
            #Create holdings object from the scores and add them to the portfolio dictionary 
            if ticker not in self.port.keys():
                self.port[ticker] = self.Holding(ticker, score)
            # Adjust position of holding of ticker
            self.port[ticker] = self.port[ticker].adjust(self.date, score, self.max_purchase)
            # Adjust portfolio cash as reflected by adjustment changes
            self.cash += self.port[ticker].change

        # Figure out how long and short portfolio is in total
        self.long_value = 0
        self.short_value = 0
        for holding in self.port.values():
            if holding.value > 0:
                self.long_value += holding.value
            else:
                self.short_value += holding.value

        #Update price of SPY
        spy_price = spy_table.at[self.date, 'SPY']
        # Position in SPY that should be taken to make portfolio as market neutral as possible
        spy_pos = -math.floor((self.long_value + self.short_value) / spy_price)
        # Hedge the portfolio via SPY with this position sizing
        self.hedge_port(spy_pos, spy_price)
    
    def hedge_port(self, spy_pos, spy_price):
        #adjust cash and position as necessary
        pos_delta = spy_pos - self.hedge
        self.cash -= pos_delta * spy_price      #if we are selling SPY, cash increases. if buying, cash decreases
        self.hedge = spy_pos
        self.hedge_val = self.hedge * spy_price

    def port_display(self):
        display(f'{self.date} : Portfolio Worth: { self.port_value( ) }')
    
    def port_holdings(self):
        for holding in self.port.values():
            holding.display()

    def port_value(self):
        self.total_value = self.cash + self.long_value + self.short_value + self.hedge_val
        return (f'Cash: {self.cash:9.2f} | Long Size: {self.long_value:9.2f} | Short Size: {self.short_value:10.2f}'
            f'| SPY Hedge: {self.hedge_val:10.2f} | Total: {self.total_value:9.2f} | Max Purchase : {self.max_purchase:9.2f}')


    class Holding(object):
        def __init__(self, ticker, score) -> None:
            #Initializing of object
            self.ticker = ticker
            self.score = score
            self.position = 0
            self.value = 0

        def adjust(self, date, score, max_purchase):
            #Update attributes of Holding object
            self.score = score
            self.date = date
            self.price = clean_table.at[self.date, self.ticker]
            self.change = 0
            if self.position == 0:      #if no position is currently held
                if self.score > 1.25:   # And the price of the security is 1.25 standard deviations above predicted value by OLS model using PCA factors
                    self.change -= self.open_short(max_purchase)    #Open a short position
                if self.score < -1.25:  # And the price of the security is 1.25 standard deviations below predicted value by OLS model using PCA factors
                    self.change -= self.open_long(max_purchase)     #Open a long position
            elif self.position < 0:
                if self.score < 0.5:    # And the price of the security is less than 0.5 standard deviations above predicted value by OLS model using PCA factors
                    self.change += self.close_short()   #Close short position
                else:
                    self.value = self.price * self.position     #simply update value of the holding
            else:
                if self.score > -0.5:   # And the price of the security is less than 0.5 standard deviations below predicted value by OLS model using PCA factors
                    self.change += self.close_long()    #Close long position
                else:
                    self.value = self.price * self.position     #simply update value of the holding
            return self

        def display(self):
            display(self.ticker + " | " + str(self.position) + " | " + str(self.value))

        def open_short(self, max_purchase):
            # Position is max integer of shares that can be short-sold given max_purchase
            self.position = -(math.floor(max_purchase / self.price))
            self.value = self.price * self.position
            return self.value

        def open_long(self, max_purchase):
            # Position is max integer of shares that can be bought given max_purchase
            self.position = (math.floor(max_purchase / self.price))
            self.value = self.price * self.position
            return self.value

        def close_long(self):
            self.value = self.position * self.price
            temp = self.value
            self.position = 0
            self.value = 0
            return temp
            

        def close_short(self):
            self.value = self.position * self.price
            temp = self.value
            self.position = 0
            self.value = 0
            return temp
        

        
        
