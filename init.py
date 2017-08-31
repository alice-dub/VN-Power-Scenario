# encoding: utf-8
# CCS in Vietnam scenarios
#
# Model framework common to all files: time domain, technology domain, units
#
# (c) Minh Ha-Duong, 2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
"""Common functions, units.

To clarify column names.

 1/ Some include Imports in electricity "Production". We don't.
    Imports are part of "Domestic Supply". We use these column names:
      Supply = Production + Import

 2/ We define Import as net of Exports

 3/ Another ambiguity is whether SmallHydro is included in "Hydro" or "Renewable"
    Here we do the former and use these column names:
      Hydro = BigHydro + SmallHydro
      BigHydro = LargeHydro + InterHydro
      Renewable = Wind + Solar + Biomass
      Renewable4 = Renewable + Small hydro

 4/ We do NOT include PumpedStorage in Hydro capacities or (double accounting) production

 5/ In VN capacity stats, generation from fuel oil and from diesel is not clearly accounted for.

 6/ Adding up fossil fuel generation capacities with renewable capacities is meaningless
    because the capacity factors are not comparable, neither are the investment costs
"""

from functools import lru_cache

#import time
import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 1000)


VERBOSE = False

show = print if VERBOSE else lambda *a, **k: None

#%% Rows

start_year = 2016
end_year = 2050
years = range(start_year, end_year + 1)
n_year = len(years)


@lru_cache(maxsize=32)
def discountor(discount_rate):
    """A vector V such that the scalar product A.V is the present value of series A."""
    return pd.Series(data=np.logspace(0, n_year - 1, n_year, base=1 / (1 + discount_rate)),
                     index=years)


def present_value(series, discount_rate):
    """Intertemporal total present value. Applies to a series or a dataframe's columns."""
    return series.mul(discountor(discount_rate), axis=0).sum()


def discount(value, year, discount_rate):
    """Return the present value of a future cash flow."""
    return value * discountor(discount_rate).loc[year]


#%% Columns
# Nuclear is presently out of the power planning discussion in Vietnam
# CCS also, but that's the point of our study.

fuels = ["Coal", "Gas", "Oil",
         "BigHydro", "SmallHydro", "Biomass", "Wind", "Solar",
         "CoalCCS", "GasCCS", "BioCCS"]

sources = fuels + ["Import"]

technologies = sources + ["PumpedStorage"]


def addcol_Renewable(container):
    """Define Renewable excluding hydro. The container can be a dict, Series, DataFrame."""
    container["Renewable"] = container["Biomass"] + container["Wind"] + container["Solar"]


def addcol_Renewable4(container):
    """Define Renewable4 including hydro. The container can be a dict, Series, DataFrame."""
    container["Renewable4"] = (container["Biomass"] + container["Wind"] + container["Solar"]
                               + container["SmallHydro"])


#%% Units

W = 1
kW = 1000
MW = 10**6
GW = 10**9
kWh = 1000
MWh = 10**6
GWh = 10**9
TWh = 10**12
Btu = 1
MBtu = 10**6
TBtu = 10**12
USD = 1
MUSD = 10**6
GUSD = 10**9
g = 10**(-3)
kg = 1
t = 1000
kt = 10**6
Mt = 10**9
Gt = 10**12

#
#def timefunc(f):
#    def f_timer(*args, **kwargs):
#        start = time.time()
#        result = f(*args, **kwargs)
#        end = time.time()
#        print(f.__name__, 'took', end - start, 'time')
#        return result
#    return f_timer
