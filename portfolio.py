#!/usr/bin/env python3
#import backtrader as bt
from dis import dis
from IPython.display import display
import pandas as pd
from datetime import datetime


clean_table = pd.read_pickle(r'./Data.pkl')

"""
class Porfolio(object):
    def __init__(self) -> None:
        self.cash = 100000   # $100,000
        self.port = { }
"""

#cash = 100000   # $100,000
#port = { }


class Portfolio(object):
    def __init__(self) -> None:
        self.cash = 100000   # $100,000
        self.port = { }
        #self.date

    def adjust_holdings(self, scores):
        #display(scores.name)
        #display(scores.values)
        self.date = scores.name
        for ticker, score in scores.items():
            #display(ticker)
            #display(score)
            if ticker not in self.port.keys():
                self.port[ticker] = self.Holding(ticker, score)
                #self.port[ticker] = self.adjust(self.port[ticker])
            #else:
            #value_delta = self.port[ticker].adjust(self.date, score)
            #self.cash += value_delta
            self.port[ticker] = self.port[ticker].adjust(self.date, score)
            self.cash += self.port[ticker].change
            #display(self.port[ticker].date.strftime('%m/%d/%Y') + " " + str(self.port[ticker].ticker) + " " + str(self.port[ticker].price) + " " + str(self.port[ticker].value))


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
            #self.date = date
            self.value = 0


        def display(self):
            #print()
            display(self.ticker + " | " + str(self.position) + " | " + str(self.value))
            #display(self.ticker)
            #display(self.score)
        
        def open_short(self):
            self.position = -1
            self.value = self.price * self.position
            #self.cash += abs(holding.value)
            return self.value

        def open_long(self):
            self.position = 1
            self.value = self.price * self.position
            #self.cash -= holding.value
            return self.value

        def close_long(self):
            #self.cash += holding.value
            temp = self.value
            self.position = 0
            self.value = 0
            return temp
            

        def close_short(self):
            #self.cash -= abs(holding.value)
            temp = self.value
            self.position = 0
            self.value = 0
            return temp
        
        def adjust(self, date, score):
            #holding.date = date
            self.score = score
            self.date = date
            self.price = clean_table.at[self.date, self.ticker]
            #display(self.date.strftime('%m/%d/%Y') + str(self.ticker) + " " + str(self.price))
            temp_value = self.value
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
            #self.value_delta = temp_value - self.value
            return self
        



#port = Portfolio()

"""
#Testing Portfolio Management
cerebro = bt.Cerebro()
cerebro.broker.setcash(100000.0)

cerebro.run()
print('Final Port Val: %.2f' % cerebro.broker.getvalue())
"""