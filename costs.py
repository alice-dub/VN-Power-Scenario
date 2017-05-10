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

from init import show, start_year, end_year, n_year, years, fuel_types
from parameters import discount_rate, plant_life
from baseline import additions, capacities_baseline, production_baseline, coal_use_baseline
from data_cost import construction_cost

pd.set_option('display.max_rows', 100)
# pd.set_option('precision', 1)


#%% Accounting functions


@lru_cache(maxsize=32)
def discountor(discount_rate):
    return pd.Series(data=np.logspace(0, n_year - 1, n_year, base=1 / (1 + discount_rate)),
                     index=years)


def present_value(series, discount_rate):
    """series can be a series or a dataframe"""
    return series.mul(discountor(discount_rate), axis=0).sum()


def discount(value, year, discount_rate):
    return value * discountor(discount_rate).loc[year]


show(discountor(discount_rate))
show()


#%% 

show("Capacities operating (MW)")
show(capacities_baseline[fuel_types])
show()

show("Electricity production (GWh)")
show(production_baseline[fuel_types + ["Import"]])
show()

show("Coal used in electricity generation (Mt)")
show(coal_use_baseline)
show()

#%% Electricity production


def show_total_power(fuel):
    value = present_value(production_baseline[fuel], discount_rate)
    value = int(value / 1000)
    show(fuel + ": " + str(value) + " TWh")

show("Baseline scenario - total electricity produced by fuel type")
show("Period: 2016 - 2050, discount rate:", discount_rate, "per year")
for fuel in fuel_types:
    show_total_power(fuel)


#%% Construction costs

show("Capacity additions (MW)")
show(additions[fuel_types].loc[start_year:])
show()

show("Overnight construction costs ($/kW)")
show(construction_cost[fuel_types])
show()

# MW * s / kW / 1000 = M$
investment_baseline = additions * construction_cost / 1000

show("Baseline scenario - Construction costs (M$)")
show(investment_baseline[fuel_types].loc[start_year:].round())
show()


#%% Residual value


def residual_value(fuel):
    lifetime = plant_life[fuel]
    idx = additions.index
    n = len(idx)
    s = pd.Series(0, index=idx, name=fuel)
    for i in range(min(lifetime, n)):
        s.iloc[n - i - 1] = 1 - (i + 1) / lifetime
    return (s * additions[fuel]).sum()

#%%


def lcoe(discount_rate, fuels):
    total_invest = present_value(investment_baseline[fuels], discount_rate).sum()
    salvage_value = discount(sum([residual_value(fuel) for fuel in fuels]),
                             end_year,
                             discount_rate)
    OM_cost = 0
    fuel_cost = 0
    total_power = present_value(production_baseline[fuels], discount_rate).sum()
#    lcoe = (investment_cost - salvage_value + OM_cost + fuel_cost) / total_power
    lcoe = (total_invest - salvage_value + OM_cost + fuel_cost) / total_power
    return fuels, lcoe, round(total_power), round(total_invest), round(salvage_value)
#    return investment_cost, salvage_value, OM_cost, fuel_cost, total_power, lcoe

show(lcoe(0.05, ["Coal"]))
show(lcoe(0.05, ["Gas"]))
show(lcoe(0.05, ["Oil"]))
show(lcoe(0.05, ["BigHydro"]))
show(lcoe(0.05, ["SmallHydro"]))
show(lcoe(0.05, ["Biomass"]))
show(lcoe(0.05, ["Wind"]))
show(lcoe(0.05, ["Solar"]))
show(lcoe(0.05, fuel_types))
