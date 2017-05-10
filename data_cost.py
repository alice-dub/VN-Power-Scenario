# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#

"""
Read-in the data files of costs from OpenEI

Transparent Cost Database  compiled and published by OpenEI
# OpenEI is developed and maintained by the National Renewable Energy Laboratory
# with funding and support from the U.S. Department of Energy and
# a network of International Parterns & Sponsors.
# http://en.openei.org/apps/TCDB/#blank
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from init import show, VERBOSE, start_year, end_year, n_year, years, fuel_types

pd.set_option('display.max_rows', 30)


#%% Construction costs
OpenEI_construction_cost_filename = "data/OpenEI/generation.capitalCost.20170510_621.csv"
OpenEI_construction_cost = pd.read_csv(OpenEI_construction_cost_filename,
                                       skiprows=[0, 2],
                                       header=0,
                                       index_col=0,
                                       usecols=["EntityId",
                                                "TechIndex",
                                                "Technology",
                                                "Year",
                                                "OnghtCptlCostDolPerKw"])

show(OpenEI_construction_cost)


def capital_cost(fuel, techindex):
    data = OpenEI_construction_cost[OpenEI_construction_cost.TechIndex == techindex]
    lm = pd.ols(x=data.Year - start_year, y=data.OnghtCptlCostDolPerKw)
    show(fuel, techindex, lm)
    cost_start_year = lm.beta.intercept
    cost_start_year_SE = lm.std_err.intercept
    trend = lm.beta.x if lm.p_value.x < 0.05 else 0
    s = pd.Series(np.linspace(cost_start_year, cost_start_year + trend * n_year, n_year),
                  index=years,
                  name=fuel).round().astype("int64")
    if VERBOSE:
        data.plot.scatter("Year",
                          "OnghtCptlCostDolPerKw",
                          title=fuel + " generation capacity overnight construction cost\n$/kW")
        plt.plot([start_year, end_year],
                 [cost_start_year, cost_start_year + trend * (n_year - 1)],
                 'r-',
                 linewidth=2.0)
        # The regression confidence interval does not show the uncertainty in data
        plt.plot([start_year, end_year],
                 [cost_start_year + 2 * cost_start_year_SE,
                  cost_start_year + trend * (n_year - 1) + 2 * cost_start_year_SE],
                 'r--',
                 linewidth=1.0)
        plt.plot([start_year, end_year],
                 [cost_start_year - 2 * cost_start_year_SE,
                  cost_start_year + trend * (n_year - 1) - 2 * cost_start_year_SE],
                 'r--',
                 linewidth=1.0)
        return int(cost_start_year), trend, s


def set_capital_cost(fuel, techindex):
    a, b, s = capital_cost(fuel, techindex)
    construction_cost_start_year[fuel], construction_cost_trend[fuel] = a, b
    construction_cost[fuel] = s

construction_cost_start_year = pd.Series(dtype="int64")
construction_cost_trend = pd.Series()
construction_cost = pd.DataFrame()

set_capital_cost("Coal", "Scrubbed")
set_capital_cost("Gas", "Combined Cycle")
set_capital_cost("Oil", "Combustion Turbine")
set_capital_cost("BigHydro", "Hydroelectric")
set_capital_cost("SmallHydro", "Small Hydropower")
set_capital_cost("Biomass", "Biopower")
set_capital_cost("Solar", "Photovoltaic")

set_capital_cost("Offshore", "Offshore")
set_capital_cost("Onshore", "Onshore")
construction_cost_start_year["Wind"] = (construction_cost_start_year["Offshore"]
                                        + construction_cost_start_year["Onshore"]) / 2
construction_cost_trend["Wind"] = (construction_cost_trend["Offshore"]
                                   + construction_cost_trend["Onshore"]) / 2
construction_cost["Wind"] = (construction_cost["Offshore"] + construction_cost["Onshore"]) // 2

show("Overnight construction costs, $/kW ", start_year)
show(construction_cost_start_year)
show()
show("Trends in overnight construction costs, $/kW/yr", start_year, "-", end_year)
show(construction_cost_trend)
show()
show("Overnight construction costs, $/kW")
show(construction_cost[fuel_types])
