# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#


"""
Assess the cost of baseline scenario

"""

import pandas as pd
import numpy as np
from functools import lru_cache
from init import show  # , VERBOSE
from data import fuel_types
from baseline import additions, capacities_baseline, production_baseline, coal_use_baseline

#%%

show("Capacity additions (MW)")
show(additions[fuel_types])
show()

show("Capacities operating (MW)")
show(capacities_baseline[fuel_types])
show()

show("Electricity production (GWh)")
show(production_baseline[fuel_types + ["Import"]])
show()

show("Coal used in electricity generation (Mt)")
show(coal_use_baseline)
show()

#%%

discount_rate = 0.05
base_year = 2016
final_year = 2050
n_year = final_year - base_year + 1


@lru_cache(maxsize=32)
def discounting_vector(discount_rate):
    return pd.Series(data=np.logspace(0, n_year - 1, n_year, base=1 / (1 + discount_rate)),
                     index=range(2016, 2051))

show(discounting_vector(0.05))
show()


def discounted_total(series, discount_rate):
    return (series * discounting_vector(discount_rate)).sum()


def show_total_power(fuel):
    value = discounted_total(production_baseline[fuel], discount_rate)
    value = int(value / 1000)
    show(fuel + ": " + str(value) + " TWh")

show("Baseline scenario - total electricity produced by fuel type")
show("Period: 2016 - 2050, discount rate:", discount_rate, "per year")
for fuel in fuel_types:
    show_total_power(fuel)
