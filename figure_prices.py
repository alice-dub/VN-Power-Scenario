# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 10:14:30 2018

@author: Alice Duval

Plot different average prices for gas and coal fuels according to
different international forecasts.

"""
import sys
import numpy as np
import matplotlib.pyplot as plt

from prices_data_international import price_coal, price_gas, coal, gas, international_prices_path
from prices_data_local import local_prices
from init import MBtu


def plot_average_prices(name, source, ax, num_forecasts):
    """Plot local prices and first international prices trajectories used in the model"""
    np.random.seed(0)
    ax.plot(np.arange(2017-len(source), 2017), source, linewidth=2.0, color='r',
             label='International past prices')
    ax.plot(np.arange(2016, 2050), local_prices[name].loc[2017:2050]* MBtu,
             linewidth=2.0, color='b', label='Local prices (Khanh N., 2017)')
    international_prices = international_prices_path(price_gas, price_coal)\
    .international_prices[name]
    ax.plot(np.arange(2015, 2050), international_prices * MBtu, color='grey',\
            label='International prices forcasts', linewidth=1.0)
    ax.set_xlabel("Year")
    ax.set_ylabel("2010 USD / MBtu")
    ax.legend(loc='upper left')
    for _ in range(num_forecasts):
        international_prices = international_prices_path(price_gas, price_coal)\
        .international_prices[name]
        ax.plot(np.arange(2015, 2050), international_prices * MBtu, linewidth=1.0)
    ax.set_title("Evolution of " + name + " prices, 1970 - 2050")

fig, axarr = plt.subplots(2, 1, figsize=[8, 12])
fig.suptitle("Coal and Gas prices forecasts", fontsize=15)

coal = [i*MBtu for i in coal]
gas = [i*MBtu for i in gas]

plot_average_prices("Coal", coal, axarr[0], 10)
plot_average_prices("Gas", gas, axarr[1], 10)

if __name__ == '__main__':
    if (len(sys.argv) == 3) and (sys.argv[1] == "plot"):
        fig.savefig(sys.argv[2])
