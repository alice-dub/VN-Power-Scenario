# encoding: utf-8
# CCS in Vietnam scenarios
#
# Physical units
#
# (c) Minh Ha-Duong, 2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
# Warning: This file should be imported before any "import natu ..."
# otherwise use_quantities does not work
#
#
VERBOSE = False

show = print if VERBOSE else lambda *a, **k: None

start_year = 2016
end_year = 2050
years = range(start_year, end_year + 1)
n_year = len(years)

fuels = ["Coal", "Gas", "Oil", "BigHydro", "SmallHydro", "Biomass", "Wind", "Solar"]
sources = fuels + ["Import"]

W = 1
kW = 1000
MW = 10**6
GWh = 10**9
TWh = 10**12
MWh = 10**6
kWh = 1000
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
