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
                                                "PublicationYear",
                                                "OnghtCptlCostDolPerKw"])


def plot_boxwhisker(data, col):
        x_min = data.Year.min()
        x_max = data.Year.max()
        x_med = (x_min + x_max) / 2
        y_median = data[col].median()
        y_quartile1 = data[col].quantile(0.25)
        y_quartile3 = data[col].quantile(0.75)
        y_max = data[col].max()
        y_min = data[col].min()
        plt.plot([x_min, x_max], [y_median, y_median], 'm', linewidth=3)
        plt.plot([x_min, x_max], [y_quartile1, y_quartile1], 'm-', linewidth=2)
        plt.plot([x_min, x_max], [y_quartile3, y_quartile3], 'm-', linewidth=2)
        plt.plot([x_min, x_min], [y_quartile1, y_quartile3], 'm-', linewidth=2)
        plt.plot([x_max, x_max], [y_quartile1, y_quartile3], 'm-', linewidth=2)
        plt.plot([x_med, x_med], [y_quartile3, y_max], 'm-', linewidth=1)
        plt.plot([x_med, x_med], [y_min, y_quartile1], 'm-', linewidth=1)


description = dict()
description["OnghtCptlCostDolPerKw"] = " generation capacity overnight construction cost\n$/kW"


def regression(df, fuel, techindex, col, no_trend):
    data = df[df.TechIndex == techindex]
    lm = pd.ols(x=data.Year - start_year, y=data[col])
    show(fuel, techindex, lm)
    cost_start_year = lm.beta.intercept
#    trend = lm.beta.x if lm.p_value.x < 0.05 else 0
    trend = 0 if no_trend or (lm.p_value.x > 0.05) else lm.beta.x
    s = pd.Series(np.linspace(cost_start_year, cost_start_year + trend * n_year, n_year),
                  index=years,
                  name=fuel).round().astype("int64")

    if VERBOSE:
        data.plot.scatter("Year", col, title=fuel + description[col])
        # Red line showing the construction costs used in model
        # Regression is both on observation and projections
        plt.plot(s.index, s.values, "r-", linewidth=2.0)
        # Magenta box and whiskers showing quartiles of observed costs
        past_data = data[data.Year < data.PublicationYear]
        plot_boxwhisker(past_data, col)
    return cost_start_year, trend, s


def set_capital_cost(fuel, techindex, no_trend=False):
    cost_start_year, trend, s = regression(OpenEI_construction_cost,
                                           fuel,
                                           techindex,
                                           "OnghtCptlCostDolPerKw",
                                           no_trend)
    construction_cost_start_year[fuel] = int(cost_start_year)
    construction_cost_trend[fuel] = trend
    construction_cost[fuel] = s

construction_cost_start_year = pd.Series(dtype="int64")
construction_cost_trend = pd.Series()
construction_cost = pd.DataFrame()

set_capital_cost("Coal", "Scrubbed")
set_capital_cost("Gas", "Combined Cycle", no_trend=True)
set_capital_cost("Oil", "Combustion Turbine")
set_capital_cost("BigHydro", "Hydroelectric")
set_capital_cost("Solar", "Photovoltaic")

# Based on too few estimates
set_capital_cost("SmallHydro", "Small Hydropower")

# Biopower: regression meaningless because of predictions incoherent with observations
set_capital_cost("Biomass", "Biopower", no_trend=True)

# In Vietnam, wind power is near-shore
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


#%%  Fixed operating costs

OpenEI_fixed_operating_cost_filename = "data/OpenEI/generation.fixedOperatingCost.20170510_612.csv"
OpenEI_fixed_operating_cost = pd.read_csv(OpenEI_fixed_operating_cost_filename,
                                          skiprows=[0, 2],
                                          header=0,
                                          index_col=0,
                                          usecols=["EntityId",
                                                   "TechIndex",
                                                   "Technology",
                                                   "Year",
                                                   "PublicationYear",
                                                   "FixedOMDolPerKw"])

description["FixedOMDolPerKw"] = " Fixed operating cost\n$/kW"


def set_fixed_operating_cost(fuel, techindex, no_trend=False):
    cost_start_year, trend, s = regression(OpenEI_fixed_operating_cost,
                                           fuel,
                                           techindex,
                                           "FixedOMDolPerKw",
                                           no_trend)
    fixed_operating_cost_start_year[fuel] = int(cost_start_year)
    fixed_operating_cost_trend[fuel] = trend
    fixed_operating_cost[fuel] = s

fixed_operating_cost_start_year = pd.Series()
fixed_operating_cost_trend = pd.Series()
fixed_operating_cost = pd.DataFrame()

set_fixed_operating_cost("Coal", "Scrubbed")
set_fixed_operating_cost("Gas", "Combined Cycle")
set_fixed_operating_cost("Oil", "Combustion Turbine", no_trend=True)
set_fixed_operating_cost("BigHydro", "Hydroelectric")
set_fixed_operating_cost("SmallHydro", "Small Hydropower")
set_fixed_operating_cost("Biomass", "Biopower", no_trend=True)
set_fixed_operating_cost("Solar", "Photovoltaic")

set_fixed_operating_cost("Offshore", "Offshore")
set_fixed_operating_cost("Onshore", "Onshore")
fixed_operating_cost_start_year["Wind"] = (fixed_operating_cost_start_year["Offshore"]
                                           + fixed_operating_cost_start_year["Onshore"]) / 2
fixed_operating_cost_trend["Wind"] = (fixed_operating_cost_trend["Offshore"]
                                      + fixed_operating_cost_trend["Onshore"]) / 2
fixed_operating_cost["Wind"] = (fixed_operating_cost["Offshore"]
                                + fixed_operating_cost["Onshore"]) / 2


show("Fixed operating costs, $/kW ", start_year)
show(fixed_operating_cost_start_year)
show()
show("Trends in fixed operating costs, $/kW/yr", start_year, "-", end_year)
show(fixed_operating_cost_trend)
show()
show("Fixed operating costs, $/kW")
show(fixed_operating_cost[fuel_types])
