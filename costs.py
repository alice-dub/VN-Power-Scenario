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

from init import show, start_year, n_year, years, fuels
from init import kW, MW, USD, MUSD, GWh, MWh

from parameters import discount_rate, plant_life
from baseline import additions, capacities_baseline, production_baseline, coal_use_baseline
from data import heat_rate
from data_cost import construction_cost, fixed_operating_cost, variable_operating_cost, fuel_price

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


#%% Electricity production

show("Electricity production (GWh)")
show(production_baseline[sources])
show()
show("Baseline scenario - total electricity produced by fuel type")
show("Period: 2016 - 2050, discount rate:", discount_rate, "per year")
for fuel in fuels:
    value = present_value(production_baseline[fuel], discount_rate)
    value = int(value / 1000)
    show(fuel + ": " + str(value) + " TWh")


#%% Construction costs

investment_baseline = additions * MW * construction_cost * USD / kW / MUSD

show("Capacity additions (MW)")
show(additions[fuels].loc[start_year:])
show()
show("Overnight construction costs ($/kW)")
show(construction_cost[fuels])
show()
show("Baseline scenario - Construction costs (M$)")
show(investment_baseline[fuels].loc[start_year:].round())
show()


#%% Residual value


def residual_value(fuel):
    lifetime = plant_life[fuel]
    idx = additions.index
    n = len(idx)
    s = pd.Series(0, index=idx, name=fuel)
    for i in range(min(lifetime, n)):
        s.iloc[n - i - 1] = 1 - (i + 0.5) / lifetime  # On average, plant opens middle of the year
    return pd.Series(data=(s * additions[fuel]).sum(), index=[2050])


#%% Fixed operating costs

fixed_operating_cost_baseline = capacities_baseline * MW * fixed_operating_cost * USD / kW / MUSD

show("Capacities operating (MW)")
show(capacities_baseline[fuels].loc[start_year:])
show()
show("Fixed operating costs ($/kW)")
show(fixed_operating_cost[fuels])
show()
show("Baseline scenario - Fixed operating costs (M$)")
show(fixed_operating_cost_baseline[fuels].loc[start_year:].round())
show()


#%% Variable operating cost

variable_operating_cost_baseline = (production_baseline * GWh
                                    * variable_operating_cost * USD / MWh
                                    / MUSD)

show("Electricity production (GWh)")
show(production_baseline[sources].loc[start_year:])
show()
show("Variable operating costs ($/kWh)")
show(variable_operating_cost[sources])
show()
show("Baseline scenario - Variable operating costs (M$)")
show(variable_operating_cost_baseline[sources].loc[start_year:].round())
show()


#%% Fuel costs

fuel_used_baseline = production_baseline * heat_rate
fuel_cost_baseline = fuel_used_baseline * fuel_price

show("Fuel price ($/??)")
show(fuel_price)
show()
show("Fuel used (??)")
show(fuel_used_baseline[sources].loc[start_year:])
show()
show("Baseline scenario - Fuel costs (M$)")
show(fuel_cost_baseline[sources].loc[start_year:].round())
show()

#%% Levelized Cost Of Electricity


def lcoe(discount_rate, cols):
    total_invest = present_value(investment_baseline[cols], discount_rate).sum()
    salvage_value = sum([present_value(residual_value(fuel), discount_rate) for fuel in cols])
    fixed_OM_cost = present_value(fixed_operating_cost_baseline[cols], discount_rate).sum()
    variable_OM_cost = present_value(variable_operating_cost_baseline[cols], discount_rate).sum()
    total_fuel_cost = present_value(fuel_cost_baseline[cols], discount_rate).sum()
    total_power = present_value(production_baseline[cols], discount_rate).sum()
    lcoe = ((total_invest - salvage_value + fixed_OM_cost + variable_OM_cost + total_fuel_cost)
            / total_power)
    return (cols, lcoe,
            [int(total_power),
             int(total_invest), int(salvage_value),
             int(fixed_OM_cost), int(variable_OM_cost), int(total_fuel_cost)]
            )

show(lcoe(0.05, ["Coal"]))
show(lcoe(0.05, ["Gas"]))
show(lcoe(0.05, ["Oil"]))
show(lcoe(0.05, ["BigHydro"]))
show(lcoe(0.05, ["SmallHydro"]))
show(lcoe(0.05, ["Biomass"]))
show(lcoe(0.05, ["Wind"]))
show(lcoe(0.05, ["Solar"]))
show(lcoe(0.05, fuels))
show(lcoe(0.05, sources))
