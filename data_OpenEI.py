# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#

"""Populate the technology database.

Each generation technology has:
- overnight construction cost
- fixed operating cost
- variable operating cost
- heat rate
which can be either
- zero
- a constant based on the median of past data
- a linear function of time based on forecasts data
The choice between these 3 methods is visual.

Energy data from OpenEI's Transparent Cost Database
+ newspaper sources for Import capacity costs
+ newspaper source Import electricity price

OpenEI is developed and maintained by the National Renewable Energy Laboratory
with funding and support from the U.S. Department of Energy and
a network of International Parterns & Sponsors.
http://en.openei.org/apps/TCDB/#blank
"""

import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

from init import pd, show, VERBOSE, start_year, end_year, n_year, years, sources

# %% Functions to build series from OpenEI data file

OpenEI = pd.read_csv("data/OpenEI/generation.lcoe.20170510_650.csv",
                     skiprows=[0, 2],
                     header=0,
                     index_col=0,
                     usecols=["EntityId",
                              "TechIndex",
                              "Technology",
                              "TechnologySubtype",
                              "Year",
                              "PublicationYear",
                              "OnghtCptlCostDolPerKw",
                              "FixedOMDolPerKw",
                              "VariableOMDolPerMwh",
                              "HeatRate"])


view = dict()

q = 'Technology == "Coal"  and '
q += 'TechnologySubtype in ["Conventional PC", "Advanced PC", "IGCC"]'
view["Coal"] = OpenEI.query(q)

q = 'Technology == "Coal" and '
q += 'TechnologySubtype in ["Advanced PC CCS", "IGCC CCS"]'
view["CoalCCS"] = OpenEI.query(q)

q = 'Technology in ["Combined Cycle", "Combustion Turbine"] and '
q += 'not TechnologySubtype == "Advanced CC CCS"'
view["Gas"] = OpenEI.query(q)

q = 'TechnologySubtype == "Advanced CC CCS"'
view["GasCCS"] = OpenEI.query(q)

q = 'Technology == "Combustion Turbine"'
view["Oil"] = OpenEI.query(q)

q = 'Technology == "Hydroelectric"'
view["BigHydro"] = OpenEI.query(q)

q = 'Technology == "Small Hydro"'
view["SmallHydro"] = OpenEI.query(q)

q = 'Technology == "Biopower"'  # Biogas, Coal co-fire, Fluidized bed, MSW, IGCC, boiler, CHP...
view["Biomass"] = OpenEI.query(q)

q = 'Technology == "Land-Based Wind"'
view["Onshore"] = OpenEI.query(q)

q = 'Technology == "Wind-Offshore"'
view["Offshore"] = OpenEI.query(q)

q = '(Technology == "Photovoltaic" and TechnologySubtype == "Utility") or '
q += 'Technology == "Solar Thermal"'
view["Solar"] = OpenEI.query(q)


def plot_boxwhisker(data, col):
    """Box and whisker plot in Magenta, meant to be overlaid on the (x=Year, y=col) plot."""
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
    """Validate graphically our derivation of technology costs from the literature.

    data: rows of the database relative to a given technology
    fuel: string, name of that technology
    col:  column of data to be plot, a kind of cost
    s:    Series, the values actually used in the model
    method: by_regression, by_median, as_zero. How  s  was derived from data[col].

    Trend line shows the costs as used in model.
    Box and whiskers shows quartiles of distribution of past costs.
    Past being relative to the date of publication of the cost.
    """
    data.plot.scatter("Year", col, title=fuel + description[col] + method)
    plt.plot(s.index, s.values, "r-", linewidth=2.0)
    plot_boxwhisker(data[data.Year < data.PublicationYear], col)


description = dict()
description["OnghtCptlCostDolPerKw"] = " generation capacity overnight construction cost\n$/kW"
description["FixedOMDolPerKw"] = " fixed operating cost\n$/kW"
description["VariableOMDolPerMwh"] = " variable operating cost\n$/MWh"
description["HeatRate"] = " heat rate\nBtu/kWh"


def as_zero(fuel, _):
    """Return a time series of zero."""
    show(fuel + " set as zero for all years")
    return pd.Series(0, index=years, name=fuel)


def by_median(fuel, col):
    """Median of observed costs, defined as 'refering to a year prior year of publication'."""
    data = view[fuel]
    past_data = data[data.Year < data.PublicationYear]
    s = pd.Series(past_data[col].median(),
                  index=years,
                  name=fuel)
    if VERBOSE:
        myplot(data, fuel, col, s, " (median of " + str(len(past_data)) + ") ")
    return s


def by_regression(fuel, col):
    """Regression, when the literature forecasts cost saving technical progress."""
    data = view[fuel]
    explaining = data.Year - start_year
    explaining = sm.add_constant(explaining)
    model = sm.OLS(data[col], explaining, missing='drop')
    results = model.fit()

    show(fuel, results.summary())
    level = results.params.const
    trend = results.params.Year if results.pvalues.Year < 0.05 else 0
    s = pd.Series(np.linspace(level, level + trend * n_year, n_year),
                  index=years,
                  name=fuel)
    if VERBOSE:
        myplot(data, fuel, col, s, " (regression on " + str(len(data)) + ") ")

    return s


# %%  Construction costs

def set_construction_cost(fuel, method):
    """Update the construction_cost dataframe for the  fuel  technology, using given  method."""
    construction_cost[fuel] = method(fuel, "OnghtCptlCostDolPerKw")


construction_cost = pd.DataFrame(index=years)

set_construction_cost("Coal", by_median)
set_construction_cost("Gas", by_median)
set_construction_cost("Oil", by_regression)
set_construction_cost("BigHydro", by_regression)
set_construction_cost("SmallHydro", by_median)
set_construction_cost("Solar", by_regression)
set_construction_cost("Biomass", by_median)

# In Vietnam, wind power is near-shore
set_construction_cost("Offshore", by_regression)
set_construction_cost("Onshore", by_regression)
construction_cost["Wind"] = (construction_cost["Offshore"] + construction_cost["Onshore"]) // 2

set_construction_cost("CoalCCS", by_regression)
set_construction_cost("GasCCS", by_median)

cost_multiplier = construction_cost["CoalCCS"] / construction_cost["Coal"]
construction_cost["BioCCS"] = construction_cost["Biomass"] * cost_multiplier


# http://www.chinadaily.com.cn/bizchina/2007-04/29/content_863786.htm
# The Wenshan-Ha Giang power transmission line is 300 kilometers long,
# its extension will transmit an average 1 billion kwh of electricity a year
# and was built at a cost of 413 million yuan (53 million U.S. dollars).
# ==>
# 10^12 Wh / 8760 = 114 MW
# 53 / 114 = 0.465 $/W = 465 $ per kW
#
#
# http://news.xinhuanet.com/english/2017-04/19/c_136220293.htm
# PREY VENG, Cambodia, April 19 (Xinhua) : The 160-km project... line
# is capable of transmitting 150 megawatts (MW) electric power
# at the cost of 75 million U.S. dollars
# ==>
# 500 $ per kW

construction_cost_start_year_import = 500
construction_cost["Import"] = pd.Series(construction_cost_start_year_import,
                                        index=years,
                                        name="Import")

show("Overnight construction costs, $/kW ", start_year)
show(construction_cost.loc[start_year].round())
show()
show("Trends in overnight construction costs, $/kW/yr", start_year, "-", end_year)
show(construction_cost.diff().loc[start_year].round(2))
show()
show("Overnight construction costs, $/kW")
show(construction_cost[sources].round())


# %%  Fixed operating costs

def set_fixed_operating_cost(fuel, method):
    """Update the fixed operating cost dataframe for the  fuel  technology, using given  method."""
    fixed_operating_cost[fuel] = method(fuel, "FixedOMDolPerKw")


fixed_operating_cost = pd.DataFrame(index=years)

set_fixed_operating_cost("Coal", by_median)
set_fixed_operating_cost("Gas", by_median)
set_fixed_operating_cost("Oil", by_median)
set_fixed_operating_cost("BigHydro", by_median)
set_fixed_operating_cost("SmallHydro", by_median)
set_fixed_operating_cost("Biomass", by_median)
set_fixed_operating_cost("Solar", by_regression)

set_fixed_operating_cost("Offshore", by_regression)
set_fixed_operating_cost("Onshore", by_regression)
fixed_operating_cost["Wind"] = (fixed_operating_cost["Offshore"]
                                + fixed_operating_cost["Onshore"]) / 2

set_fixed_operating_cost("CoalCCS", by_median)
set_fixed_operating_cost("GasCCS", by_median)

cost_multiplier = fixed_operating_cost["CoalCCS"] / fixed_operating_cost["Coal"]
fixed_operating_cost["BioCCS"] = fixed_operating_cost["Biomass"] * cost_multiplier

set_fixed_operating_cost("Import", as_zero)

show("Fixed operating costs, $/kW ", start_year)
show(fixed_operating_cost.loc[start_year].round())
show()
show("Trends in fixed operating costs, $/kW/yr", start_year, "-", end_year)
show(fixed_operating_cost.diff().loc[start_year].round(2))
show()
show("Fixed operating costs, $/kW")
show(fixed_operating_cost[sources].round())


# %%  Variable operating costs

def set_variable_operating_cost(fuel, method=by_median):
    """Update the variabale operating cost dataframe for the  fuel  technology, using  method."""
    variable_operating_cost[fuel] = method(fuel, "VariableOMDolPerMwh")


variable_operating_cost = pd.DataFrame(index=years)

set_variable_operating_cost("Coal")
set_variable_operating_cost("Gas")
set_variable_operating_cost("Oil")
set_variable_operating_cost("BigHydro")
set_variable_operating_cost("SmallHydro")
set_variable_operating_cost("Biomass")
set_variable_operating_cost("Solar")

set_variable_operating_cost("Offshore")
set_variable_operating_cost("Onshore")
variable_operating_cost["Wind"] = variable_operating_cost["Offshore"]

set_variable_operating_cost("CoalCCS")
set_variable_operating_cost("GasCCS")

cost_multiplier = variable_operating_cost["CoalCCS"] / variable_operating_cost["Coal"]
variable_operating_cost["BioCCS"] = variable_operating_cost["Biomass"] * cost_multiplier

# $/MW,  Price of imports from China in 2012
# Source  http://www.globaltimes.cn/content/888455.shtml
variable_operating_cost_start_year_import = 60.8
variable_operating_cost["Import"] = pd.Series(variable_operating_cost_start_year_import,
                                              index=years,
                                              name="Import")

show("Variable operating costs (constant over time), $/MW ", start_year)
show(variable_operating_cost.loc[start_year].round(2))
show()


# %% Heat rate

def set_heat_rate(fuel, method=by_median):
    """Update the heat_rate dataframe for the  fuel  technology."""
    heat_rate[fuel] = method(fuel, "HeatRate")


heat_rate = pd.DataFrame(index=years)

set_heat_rate("Coal")
set_heat_rate("Gas")
set_heat_rate("Oil")
set_heat_rate("BigHydro", as_zero)
set_heat_rate("SmallHydro", as_zero)
set_heat_rate("Biomass")
set_heat_rate("Solar", as_zero)
set_heat_rate("Wind", as_zero)
set_heat_rate("Import", as_zero)


# %% Fuel prices

heat_price = pd.DataFrame(index=years)

# $/MBtu, http://en.openei.org/apps/TCDB/levelized_cost_calculations.html
# In controlled environment (China in the 50-70, Vietnam now), fossil fuel prices grow stable
# In market they swing with the balance of supply and demand
# But there is little empirical evidence about any long term trend
#.
heat_price["Coal"] = pd.Series(2.34, index=years)
heat_price["Gas"] = pd.Series(4.4, index=years)
heat_price["Oil"] = pd.Series(4.4, index=years)
heat_price["BigHydro"] = pd.Series(0, index=years)
heat_price["SmallHydro"] = pd.Series(0, index=years)
heat_price["Biomass"] = pd.Series(2.27, index=years)
heat_price["Wind"] = pd.Series(0, index=years)
heat_price["Solar"] = pd.Series(0, index=years)
heat_price["Import"] = pd.Series(0, index=years)
