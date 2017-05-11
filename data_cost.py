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

from init import show, VERBOSE, start_year, end_year, n_year, years, fuels, sources

pd.set_option('display.max_rows', 30)


#%% Functions to build series from OpenEI data files


def read_OpenEI(filename, variablename):
    return pd.read_csv(filename,
                       skiprows=[0, 2],
                       header=0,
                       index_col=0,
                       usecols=["EntityId",
                                "TechIndex",
                                "Technology",
                                "Year",
                                "PublicationYear",
                                variablename])


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


def myplot(data, fuel, col, s, method):
        data.plot.scatter("Year", col, title=fuel + description[col] + method)
        # Red line showing the construction costs used in model
        plt.plot(s.index, s.values, "r-", linewidth=2.0)
        # Magenta box and whiskers showing quartiles of observed costs
        plot_boxwhisker(data[data.Year < data.PublicationYear], col)

description = dict()
description["OnghtCptlCostDolPerKw"] = " generation capacity overnight construction cost\n$/kW"
description["FixedOMDolPerKw"] = " fixed operating cost\n$/kW"
description["VariableOMDolPerMwh"] = " variable operating cost\n$/MWh"


def by_median(df, fuel, techindex, col):
    data = df[df.TechIndex == techindex]
    past_data = data[data.Year < data.PublicationYear]
    cost_start_year = past_data[col].median()
    s = pd.Series(cost_start_year, index=years, name=fuel)
    if VERBOSE:
        myplot(data, fuel, col, s, " (median of " + str(len(past_data)) + ") " + techindex)
    return cost_start_year, 0, s


def by_regression(df, fuel, techindex, col):
    data = df[df.TechIndex == techindex]
    lm = pd.ols(x=data.Year - start_year, y=data[col])
    show(fuel, techindex, lm)
    cost_start_year = lm.beta.intercept
    trend = lm.beta.x if lm.p_value.x < 0.05 else 0
    s = pd.Series(np.linspace(cost_start_year, cost_start_year + trend * n_year, n_year),
                  index=years,
                  name=fuel)
    if VERBOSE:
        myplot(data, fuel, col, s, " (regression on " + str(len(data)) + ") " + techindex)
    return cost_start_year, trend, s

#%%

construction_cost_filename = "data/OpenEI/generation.capitalCost.20170510_621.csv"
OpenEI_construction_cost = read_OpenEI(construction_cost_filename, "OnghtCptlCostDolPerKw")


def set_capital_cost(fuel, techindex, method):
    cost_start_year, trend, s = method(OpenEI_construction_cost,
                                       fuel,
                                       techindex,
                                       "OnghtCptlCostDolPerKw")
    construction_cost_start_year[fuel] = int(cost_start_year)
    construction_cost_trend[fuel] = trend
    construction_cost[fuel] = s.round().astype("int64")

construction_cost_start_year = pd.Series(dtype="int64")
construction_cost_trend = pd.Series()
construction_cost = pd.DataFrame()

set_capital_cost("Coal", "Scrubbed", by_median)
set_capital_cost("Gas", "Combined Cycle", by_median)
set_capital_cost("Oil", "Combustion Turbine", by_regression)
set_capital_cost("BigHydro", "Hydroelectric", by_regression)
set_capital_cost("SmallHydro", "Small Hydropower", by_median)
set_capital_cost("Solar", "Photovoltaic", by_regression)

# Biopower: regression meaningless because of predictions incoherent with observations
set_capital_cost("Biomass", "Biopower", by_median)

# In Vietnam, wind power is near-shore
set_capital_cost("Offshore", "Offshore", by_regression)
set_capital_cost("Onshore", "Onshore", by_regression)
construction_cost_start_year["Wind"] = (construction_cost_start_year["Offshore"]
                                        + construction_cost_start_year["Onshore"]) / 2
construction_cost_trend["Wind"] = (construction_cost_trend["Offshore"]
                                   + construction_cost_trend["Onshore"]) / 2
construction_cost["Wind"] = (construction_cost["Offshore"] + construction_cost["Onshore"]) // 2


# http://www.chinadaily.com.cn/bizchina/2007-04/29/content_863786.htm
"""The Wenshan-Ha Giang power transmission line is 300 kilometers long, 
its extension will transmit an average 1 billion kwh of electricity a year
and was built at a cost of 413 million yuan (53 million U.S. dollars).
==>
10^12 Wh / 8760 = 114 MW
53 / 114 = 0.465 $/W = 465 $ per kW
"""

# http://news.xinhuanet.com/english/2017-04/19/c_136220293.htm
"""PREY VENG, Cambodia, April 19 (Xinhua) : The 160-km project... line
is capable of transmitting 150 megawatts (MW) electric power
at the cost of 75 million U.S. dollars
==>
500 $ per kW"""

construction_cost_start_year["Import"] = 500
construction_cost_trend["Import"] = 0
construction_cost["Import"] = pd.Series(construction_cost_start_year["Import"],
                                        index=years,
                                        name="Import")

show("Overnight construction costs, $/kW ", start_year)
show(construction_cost_start_year)
show()
show("Trends in overnight construction costs, $/kW/yr", start_year, "-", end_year)
show(construction_cost_trend)
show()
show("Overnight construction costs, $/kW")
show(construction_cost[sources])


#%%  Fixed operating costs

fixed_operating_cost_filename = "data/OpenEI/generation.fixedOperatingCost.20170510_612.csv"
OpenEI_fixed_operating_cost = read_OpenEI(fixed_operating_cost_filename, "FixedOMDolPerKw")


def set_fixed_operating_cost(fuel, techindex, method):
    cost_start_year, trend, s = method(OpenEI_fixed_operating_cost,
                                       fuel,
                                       techindex,
                                       "FixedOMDolPerKw")
    fixed_operating_cost_start_year[fuel] = int(cost_start_year)
    fixed_operating_cost_trend[fuel] = trend
    fixed_operating_cost[fuel] = s.round().astype("int64")

fixed_operating_cost_start_year = pd.Series()
fixed_operating_cost_trend = pd.Series()
fixed_operating_cost = pd.DataFrame()

set_fixed_operating_cost("Coal", "Scrubbed", by_regression)
set_fixed_operating_cost("Gas", "Combined Cycle", by_regression)
set_fixed_operating_cost("Oil", "Combustion Turbine", by_median)
set_fixed_operating_cost("BigHydro", "Hydroelectric", by_regression)
set_fixed_operating_cost("SmallHydro", "Small Hydropower", by_median)
set_fixed_operating_cost("Biomass", "Biopower", by_median)
set_fixed_operating_cost("Solar", "Photovoltaic", by_regression)

set_fixed_operating_cost("Offshore", "Offshore", by_regression)
set_fixed_operating_cost("Onshore", "Onshore", by_regression)
fixed_operating_cost_start_year["Wind"] = (fixed_operating_cost_start_year["Offshore"]
                                           + fixed_operating_cost_start_year["Onshore"]) / 2
fixed_operating_cost_trend["Wind"] = (fixed_operating_cost_trend["Offshore"]
                                      + fixed_operating_cost_trend["Onshore"]) / 2
fixed_operating_cost["Wind"] = (fixed_operating_cost["Offshore"]
                                + fixed_operating_cost["Onshore"]) / 2


# TODO: get data on maintenance costs for the transboundary transmission lines !
fixed_operating_cost_start_year["Import"] = 0
fixed_operating_cost_trend["Import"] = 0
fixed_operating_cost["Import"] = pd.Series(fixed_operating_cost_start_year["Import"],
                                           index=years,
                                           name="Import")


show("Fixed operating costs, $/kW ", start_year)
show(fixed_operating_cost_start_year)
show()
show("Trends in fixed operating costs, $/kW/yr", start_year, "-", end_year)
show(fixed_operating_cost_trend)
show()
show("Fixed operating costs, $/kW")
show(fixed_operating_cost[sources])


#%%  Variable operating costs

variable_opcost_filename = "data/OpenEI/generation.variableOperatingCost.20170510_621.csv"
OpenEI_variable_operating_cost = read_OpenEI(variable_opcost_filename, "VariableOMDolPerMwh")


def set_variable_operating_cost(fuel, techindex):
    cost_start_year, trend, s = by_median(OpenEI_variable_operating_cost,
                                          fuel,
                                          techindex,
                                          "VariableOMDolPerMwh")
    variable_operating_cost_start_year[fuel] = cost_start_year
    variable_operating_cost[fuel] = s

variable_operating_cost_start_year = pd.Series()
variable_operating_cost = pd.DataFrame()

set_variable_operating_cost("Coal", "Scrubbed")
set_variable_operating_cost("Gas", "Combined Cycle")
set_variable_operating_cost("Oil", "Combustion Turbine")
set_variable_operating_cost("BigHydro", "Hydroelectric")
set_variable_operating_cost("SmallHydro", "Small Hydropower")
set_variable_operating_cost("Biomass", "Biopower")

set_variable_operating_cost("Offshore", "Offshore")
set_variable_operating_cost("Onshore", "Onshore")
variable_operating_cost_start_year["Wind"] = (variable_operating_cost_start_year["Offshore"]
                                              + variable_operating_cost_start_year["Onshore"]) / 2
variable_operating_cost["Wind"] = (variable_operating_cost["Offshore"]
                                   + variable_operating_cost["Onshore"]) / 2

variable_operating_cost_start_year["Solar"] = 0
variable_operating_cost["Solar"] = pd.Series(0, index=years, name="Solar")

variable_operating_cost_start_year["Import"] = 0
variable_operating_cost["Import"] = pd.Series(0, index=years, name="Import")

show("Variable operating costs (constant over time), $/MW ", start_year)
show(variable_operating_cost_start_year)
show()


#%% Fuel prices

fuel_price = pd.DataFrame(index=years)

fuel_price["Coal"] = 0
fuel_price["Gas"] = 0
fuel_price["Oil"] = 0
fuel_price["BigHydro"] = 0
fuel_price["SmallHydro"] = 0
fuel_price["Biomass"] = 0
fuel_price["Wind"] = 0
fuel_price["Solar"] = 0
fuel_price["Import"] = 60.8   # $/MW,  Source  http://www.globaltimes.cn/content/888455.shtml
