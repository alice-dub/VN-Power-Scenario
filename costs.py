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

from init import show, start_year, end_year, n_year, years, fuels, sources
from init import runId, run_locals, run_globals
from init import kW, MW, USD, MUSD, GWh, MWh, kWh, Btu, MBtu, TBtu, g, kt, Mt, Gt

from parameters import discount_rate, plant_life
from baseline import additions, capacities_baseline, production_baseline
from data_cost import construction_cost, fixed_operating_cost, variable_operating_cost
from data_cost import heat_rate, heat_price, emission_factor


pd.set_option('display.max_rows', 100)
# pd.set_option('precision', 1)

show(runId)

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
    remaining_fraction = pd.Series(0, index=idx)
    for i in range(min(lifetime, n)):
        # On average, plant opens middle of the year
        remaining_fraction.iloc[n - i - 1] = 1 - (i + 0.5) / lifetime
    s = pd.Series(0, index=years, name=fuel)
    s[2050] = (remaining_fraction * additions[fuel]).sum()
    return s

salvage_value_baseline = pd.concat([residual_value(fuel) for fuel in sources], axis=1)

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

heat_used_baseline = production_baseline * GWh * heat_rate * Btu / kWh / TBtu
fuel_cost_baseline = heat_used_baseline * TBtu * heat_price * USD / MBtu / MUSD

show("Heat price ($/MBtu)")
show(heat_price)
show()
show("Heat used (TBtu)")
show(heat_used_baseline[sources].loc[start_year:].round())
show()
show("Baseline scenario - Fuel costs (M$)")
show(fuel_cost_baseline[sources].loc[start_year:].round())
show()


#%% Levelized Cost Of Electricity


def pv(variable, cols, discount_rate):
    return present_value(variable[cols], discount_rate).sum()


def lcoe(discount_rate, cols):
    """Returns the Levelized Cost Of Electricity,
       computed at the national system level on 2016-2050 period

       The function also returns a runId number, to access details on the model run
    """
    total_invest = pv(investment_baseline, cols, discount_rate)
    salvage_value = pv(salvage_value_baseline, cols, discount_rate)
    fixed_OM_cost = pv(fixed_operating_cost_baseline, cols, discount_rate)
    variable_OM_cost = pv(variable_operating_cost_baseline, cols, discount_rate)
    total_fuel_cost = pv(fuel_cost_baseline, cols, discount_rate)
    total_power = pv(production_baseline, cols, discount_rate)

    lcoe = ((total_invest - salvage_value + fixed_OM_cost + variable_OM_cost + total_fuel_cost)
            / total_power)

    # Store details in a global cache
    global runId
    runId += 1
    run_locals[runId] = locals()
    run_globals[runId] = {k: v for k, v in globals().items() if not k.startswith('_')}
    return lcoe, cols, runId

show(lcoe(0.05, ["Coal"]))
show(lcoe(0.05, ["Gas"]))
show(lcoe(0.05, ["Oil"]))
show(lcoe(0.05, ["BigHydro"]))
show(lcoe(0.05, ["SmallHydro"]))
show(lcoe(0.05, ["Biomass"]))
show(lcoe(0.05, ["Wind"]))
show(lcoe(0.05, ["Solar"]))
show(lcoe(0.05, ["Import"]))
show(lcoe(0.05, fuels))
show(lcoe(0.05, sources))


#%% CO2

emissions_baseline = production_baseline * GWh * emission_factor * g / kWh / kt

show(emissions_baseline[sources])
show()
show("Sum of CO2eq emissions over ", start_year, "-", end_year, " (Mt)")
show((emissions_baseline.sum() * kt / Mt).round())
show()
show("Total emissions = ", (emissions_baseline.sum().sum() * kt / Gt).round(), " Gt CO2eq")
