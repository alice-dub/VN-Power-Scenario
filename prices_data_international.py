# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 11:44:08 2018

@author: Alice Duval

Prices are in $/mt (in 2017 US dollars and metric ton) for Coal based on Australian prices and
in $/mmbtu for Gas based on Japan prices.

Data come from World Bank forecasts

ISSUES TO SOLVE : What happens for 2015 ? (We are not interested in this year -> to araise)
"""

import numpy as np
from init import pd, start_year, end_year, t, MBtu, calorific_power

#Collect of data
international_prices_data = pd.read_csv("data/Oil_Gas_prices/data_prices_international.csv",
                        index_col=0)

international_prices_data.columns = ["Coal", "Gas"]

x = np.array(international_prices_data.index)
y_coal = np.array(international_prices_data.Coal) / (calorific_power["Coal_international"] * t)
y_gas = np.array(international_prices_data.Gas) / MBtu

#interpolation of data with a langrangian polynom

interpol_coal_price = []
interpol_gas_price = []
index = []

#Saving interpolating data

#Between 2025 and 2030 : Linear interpolation

#director coefficent
m_coal = (y_coal[-1]-y_coal[-2])/(x[-1]-x[-2])
m_gas = (y_gas[-1]-y_gas[-2])/(x[-1]-x[-2])
#origin value
p_coal = y_coal[-1] - m_coal * x[-1]
p_gas = y_gas[-1] - m_gas * x[-1]

for i in range(start_year, end_year+1):
    if i <= 2025:
        interpol_coal_price.append(y_coal[i-start_year+1])
        interpol_gas_price.append(y_gas[i-start_year+1])
    elif i <= 2030:
        interpol_coal_price.append(m_coal * (i) + p_coal)
        interpol_gas_price.append(m_gas * (i) + p_gas)
    else:
        interpol_coal_price.append(interpol_coal_price[-1])
        interpol_gas_price.append(interpol_gas_price[-1])

international_prices = pd.DataFrame({'Coal': interpol_coal_price,
                                      'Gas': interpol_gas_price},
    index=range(start_year, end_year+1))


