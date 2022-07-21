#!/usr/bin/env python3
#import backtrader as bt
from dis import dis
from IPython.display import display
import pandas as pd
from datetime import datetime


clean_table = pd.read_pickle(r'./Data.pkl')


port = { }

def adjust_holdings(scores):
    #display(scores.name)
    #display(scores.values)
    for ticker, score in scores.items():
        #display(ticker)
        #display(score)
        if ticker not in port.keys():
            port[ticker] = Holding(ticker, score, scores.name)

def port_display():
    for holding in port.values():
        holding.display()

class Holding(object):
    def __init__(self, ticker, score, date) -> None:
        self.ticker = ticker
        self.score = score
        self.position = 0
        self.date = date
        self.value = 0
        self.adjust(self.date)

    #def update(self, price):
    #   self.price = price

    def display(self):
        print()
        display(self.date.strftime('%m/%d/%Y') + ": " + self.ticker + " | " + str(self.position) + " | " + str(self.value))
        #display(self.ticker)
        #display(self.score)

    def adjust(self, date):
        self.price = clean_table.at[date, self.ticker]
        if self.position == 0:
            if self.score > 1.25:
                self.open_short()
            if self.score < -1.25:
                self.open_long()
        elif self.position > 0:
            if self.score < 0.5:
                self.close_short()
            else:
                pass
        else:
            if self.score > -0.5:
                self.close_long()
            else:
                pass
    
    def open_short(self):
        self.position = -1
        self.value = self.price * self.position

    def open_long(self):
        self.position = 1
        self.value = self.price * self.position

    def close_long(self):
        self.position = 0
        self.value = 0

    def close_short(self):
        self.position = 0
        self.value = 0


"""
#Testing Portfolio Management
cerebro = bt.Cerebro()
cerebro.broker.setcash(100000.0)

cerebro.run()
print('Final Port Val: %.2f' % cerebro.broker.getvalue())
"""