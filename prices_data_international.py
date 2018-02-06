# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 11:44:08 2018

@author: Alice Duval

Prices are in $/mt (in 2017 US dollars and metric ton) for Coal based on Australian prices and
in $/mmbtu for Gas based on Japan prices.

Data come from World Bank database

ISSUE TO SOLVE : These prices are smaller than local prices
"""

import sys

import numpy as np
from scipy.stats import norm
from init import pd, start_year, end_year, t, MBtu, calorific_power


#%%Monte Carlo characteristics : 35 forcasted prices from 2016 to 2050
for_values = end_year - start_year +1

#Collect of data

international_prices_data = pd.read_csv("data/Oil_Gas_prices/data_prices_international_past.csv",
                        index_col=0)

international_prices_data.columns = ["Gas", "Coal"]

x = np.array(international_prices_data.index)
y_coal = np.array(international_prices_data.Coal) / (calorific_power["Coal_international"] * t)
y_gas = np.array(international_prices_data.Gas) / MBtu

price_gas = pd.DataFrame({'Price_Gas': international_prices_data['Gas']}).loc[1977:2016] / (MBtu)
price_coal = pd.DataFrame({'Price_Coal': international_prices_data['Coal']}).loc[1970:2016]\
/(calorific_power["Coal_international"] * t)
coal = []
gas = []
for j in range(len(price_coal)):
    coal.append(np.array(price_coal)[j][0])
for j in range(len(price_gas)):
    gas.append(np.array(price_gas)[j][0])

def x_function(prices):
    "Define a sequence used in correlation factor calculation"
    x_list = []
    for i, n in enumerate(prices):
        if i < len(prices)-1:
            x_list.append(np.log(n / prices[i+1]))
    return x_list

def average_coeff(sequence):
    "Calculate the average of a sequence"
    return  1 / len(sequence) * np.sum(sequence)

def random():
    "Generate random number for N(0,1) distribution"
    return norm.ppf(np.random.rand(for_values, 1))

def log_returns(data):
    "Calculate the log return of a time serie"
    log_ret = np.log(1 + data.pct_change()).loc[1978:2016]
    u = log_ret.mean()
    var = log_ret.var()
    drift = u - (0.5 * var)
    stdev = log_ret.std()
    return drift.values[0], stdev.values[0]

class international_prices_path():
    """ An international prices forecast, based on historical data and geometric brownian
    movement"""

    def __init__(self, past_gas, past_coal):
        self.past_gas = past_gas
        self.past_coal = past_coal
        self.coef_cor = self.realized_pairwise_correlation()
        self.forecast_price = self.price_path()
        self.international_prices = pd.DataFrame({'Coal': self.forecast_price[1],
                                      'Gas': self.forecast_price[0]},
        index=range(start_year, end_year+1))

    def realized_pairwise_correlation(self):
        "Calculate the correlation factor of past data"
        c_coal = [c[0] for c in np.array(self.past_coal)[7:]]
        c_gas = [g[0] for g in np.array(self.past_gas)]
        x_gas = x_function(c_gas)
        x_coal = x_function(c_coal)
        av_gas = average_coeff(x_gas)
        av_coal = average_coeff(x_coal)
        coef_gas = []
        coef_coal = []

        for i, _ in enumerate(x_gas):
            coef_gas.append(x_gas[i] - av_gas)
            coef_coal.append(x_coal[i] - av_coal)

        coef_cor = sum(a * b for (a, b)\
                       in zip(coef_gas, coef_coal)) / np.sqrt(sum(a * b for (a, b)\
                                  in zip(coef_gas, coef_gas)) * sum(a * b for (a, b) \
                                        in zip(coef_coal, coef_coal)))
        return coef_cor

    def price_path(self):
        "Generate two correlated prices paths"
        b = [random(), random()]
        drift = [log_returns(self.past_gas)[0], log_returns(self.past_coal)[0]]
        stdev = [log_returns(self.past_gas)[1], log_returns(self.past_coal)[1]]
        yearly_returns = [np.exp(drift[0] + stdev[0] * b[0]), np.exp(drift[1] + stdev[1] *
                          (self.coef_cor * b[0] + np.sqrt(1-self.coef_cor**2) * b[1]))]

        price_list = [np.zeros_like(yearly_returns)[0], np.zeros_like(yearly_returns)[1]]
        last_price = [self.past_gas.iloc[-1], self.past_coal.iloc[-1]]
        price_list[0][0] = last_price[0][0]
        price_list[1][0] = last_price[1][0]

        for i in range(1, for_values):
            price_list[0][i] = price_list[0][i - 1] * yearly_returns[0][i]
            price_list[1][i] = price_list[1][i - 1] * yearly_returns[1][i]

        for_coal = []
        for_gas = []
        for i in range(start_year, end_year+1):
            for_coal.append(price_list[1][i-start_year][0])
            for_gas.append(price_list[0][i-start_year][0])

        return for_gas, for_coal

    def summary(self):
        return ("Gaz prices\n" +
                "Drift value : " + str(round(log_returns(self.past_gas)[0], 3)) + "\n" +
                "Standard Deviation : " + str(round(log_returns(self.past_gas)[1], 2))+"\n\n"+
                "Coal prices\n" +
                "Drift value : " + str(round(log_returns(self.past_coal)[0], 3)) + "\n" +
                "Standard Deviation : " + str(round(log_returns(self.past_coal)[1], 2)) +
                "\n\n" +
                "Correlation factor between the two series: " + str(round(self.coef_cor, 2)) + "\n"
                )

    def summarize(self):
        print(self.summary())



if __name__ == '__main__':
    if (len(sys.argv) == 2) and (sys.argv[1] == "summarize"):
        print("""
              ******************************************
              ***   Past data characteristics   ***
              ******************************************
              """)
        international_prices_path(price_gas, price_coal).summarize()
