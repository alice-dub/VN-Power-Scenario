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

from init import show, VERBOSE, start_year, end_year, n_year, years, sources

pd.set_option('display.max_rows', 30)


#%% Functions to build series from OpenEI data file

OpenEI = pd.read_csv("data/OpenEI/generation.lcoe.20170510_650.csv",
                     skiprows=[0, 2],
                     header=0,
                     index_col=0,
                     usecols=["EntityId",
                              "TechIndex",
                              "Technology",
                              "Year",
                              "PublicationYear",
                              "OnghtCptlCostDolPerKw",
                              "FixedOMDolPerKw",
                              "VariableOMDolPerMwh",
                              "HeatRate"])

techindex = {"Coal": "Scrubbed",
             "Gas": "Combined Cycle",
             "Oil": "Combustion Turbine",
             "BigHydro": "Hydroelectric",
             "SmallHydro": "Small Hydropower",
             "Biomass": "Biopower",
             "Wind": "Offshore",
             "Offshore": "Offshore",
             "Onshore": "Offshore",
             "Solar": "Photovoltaic"}


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
description["HeatRate"] = " heat rate\nBtu/kWh"


def as_zero(fuel, col):
    show(fuel + " set as zero for all years")
    return 0, 0, pd.Series(0, index=years, name=fuel)


def by_median(fuel, col):
    data = OpenEI[OpenEI.TechIndex == techindex[fuel]]
    past_data = data[data.Year < data.PublicationYear]
    level = past_data[col].median()
    s = pd.Series(level, index=years, name=fuel)
    if VERBOSE:
        myplot(data, fuel, col, s, " (median of " + str(len(past_data)) + ") " + techindex[fuel])
    return level, 0, s


def by_regression(fuel, col):
    data = OpenEI[OpenEI.TechIndex == techindex[fuel]]
    lm = pd.ols(x=data.Year - start_year, y=data[col])
    show(fuel, techindex[fuel], lm)
    level = lm.beta.intercept
    trend = lm.beta.x if lm.p_value.x < 0.05 else 0
    s = pd.Series(np.linspace(level, level + trend * n_year, n_year),
                  index=years,
                  name=fuel)
    if VERBOSE:
        myplot(data, fuel, col, s, " (regression on " + str(len(data)) + ") " + techindex[fuel])
    return level, trend, s

#%%


def set_capital_cost(fuel, method):
    level, trend, s = method(fuel, "OnghtCptlCostDolPerKw")
    construction_cost_start_year[fuel] = level
    construction_cost_trend[fuel] = trend
    construction_cost[fuel] = s

construction_cost_start_year = pd.Series()
construction_cost_trend = pd.Series()
construction_cost = pd.DataFrame()

set_capital_cost("Coal", by_median)
set_capital_cost("Gas", by_median)
set_capital_cost("Oil", by_regression)
set_capital_cost("BigHydro", by_regression)
set_capital_cost("SmallHydro", by_median)
set_capital_cost("Solar", by_regression)

# Biopower: regression meaningless because of predictions incoherent with observations
set_capital_cost("Biomass", by_median)

# In Vietnam, wind power is near-shore
set_capital_cost("Offshore", by_regression)
set_capital_cost("Onshore", by_regression)
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


def set_fixed_operating_cost(fuel, method):
    level, trend, s = method(fuel, "FixedOMDolPerKw")
    fixed_operating_cost_start_year[fuel] = level
    fixed_operating_cost_trend[fuel] = trend
    fixed_operating_cost[fuel] = s

fixed_operating_cost_start_year = pd.Series()
fixed_operating_cost_trend = pd.Series()
fixed_operating_cost = pd.DataFrame()

set_fixed_operating_cost("Coal", by_regression)
set_fixed_operating_cost("Gas", by_regression)
set_fixed_operating_cost("Oil", by_median)
set_fixed_operating_cost("BigHydro", by_regression)
set_fixed_operating_cost("SmallHydro", by_median)
set_fixed_operating_cost("Biomass", by_median)
set_fixed_operating_cost("Solar", by_regression)

set_fixed_operating_cost("Offshore", by_regression)
set_fixed_operating_cost("Onshore", by_regression)
fixed_operating_cost_start_year["Wind"] = (fixed_operating_cost_start_year["Offshore"]
                                           + fixed_operating_cost_start_year["Onshore"]) / 2
fixed_operating_cost_trend["Wind"] = (fixed_operating_cost_trend["Offshore"]
                                      + fixed_operating_cost_trend["Onshore"]) / 2
fixed_operating_cost["Wind"] = (fixed_operating_cost["Offshore"]
                                + fixed_operating_cost["Onshore"]) / 2


# TODO: get data on maintenance costs for the transboundary transmission lines !
set_fixed_operating_cost("Import", as_zero)

show("Fixed operating costs, $/kW ", start_year)
show(fixed_operating_cost_start_year)
show()
show("Trends in fixed operating costs, $/kW/yr", start_year, "-", end_year)
show(fixed_operating_cost_trend)
show()
show("Fixed operating costs, $/kW")
show(fixed_operating_cost[sources])


#%%  Variable operating costs


def set_variable_operating_cost(fuel, method=by_median):
    level, trend, s = method(fuel, "VariableOMDolPerMwh")
    variable_operating_cost_start_year[fuel] = level
    variable_operating_cost[fuel] = s

variable_operating_cost_start_year = pd.Series()
variable_operating_cost = pd.DataFrame()

set_variable_operating_cost("Coal")
set_variable_operating_cost("Gas")
set_variable_operating_cost("Oil")
set_variable_operating_cost("BigHydro")
set_variable_operating_cost("SmallHydro")
set_variable_operating_cost("Biomass")
set_variable_operating_cost("Solar")
set_variable_operating_cost("Wind")

# $/MW,  Price of imports from China in 2012
# Source  http://www.globaltimes.cn/content/888455.shtml
variable_operating_cost_start_year["Import"] = 60.8
variable_operating_cost["Import"] = pd.Series(variable_operating_cost_start_year["Import"],
                                              index=years,
                                              name="Import")

show("Variable operating costs (constant over time), $/MW ", start_year)
show(variable_operating_cost_start_year)
show()


#%% Heat rate


def set_heat_rate(fuel, method=by_median):
    level, trend, s = method(fuel, "HeatRate")
    heat_rate_start_year[fuel] = level
    heat_rate_trend[fuel] = trend
    heat_rate[fuel] = s

heat_rate_start_year = pd.Series()
heat_rate_trend = pd.Series()
heat_rate = pd.DataFrame()

set_heat_rate("Coal")
set_heat_rate("Gas")
set_heat_rate("Oil")
set_heat_rate("BigHydro", as_zero)
set_heat_rate("SmallHydro", as_zero)
set_heat_rate("Biomass")
set_heat_rate("Solar", as_zero)
set_heat_rate("Wind", as_zero)
set_heat_rate("Import", as_zero)

show(heat_rate)
show()

#%% Fuel prices

heat_price = pd.DataFrame(index=years)

# $/MBtu, http://en.openei.org/apps/TCDB/levelized_cost_calculations.html
heat_price["Coal"] = 2.34
heat_price["Gas"] = 4.4
heat_price["Oil"] = 4.4
heat_price["BigHydro"] = 0
heat_price["SmallHydro"] = 0
heat_price["Biomass"] = 2.27
heat_price["Wind"] = 0
heat_price["Solar"] = 0
heat_price["Import"] = 0


#%% Emission factors

#Source : IPCC SRREN
# Table A.II.4 | Aggregated results of literature review of LCAs of GHG emissions
# from electricity generation technologies (g CO2eq/kWh)
# Median of the literature reviewed
emission_factor = pd.Series({"Coal": 1001, "Gas": 469, "Oil": 840, "BigHydro": 4,
                             "SmallHydro": 4, "Biomass": 18, "Wind": 12, "Solar": 46})

#Assumption: VN imports from China and Lao
emission_factor["Import"] = 0.5 * emission_factor["Coal"] + 0.5 * emission_factor["BigHydro"]
