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

runId = 0
run_locals = dict()
run_globals = dict()

#from natu import config
## config.use_quantities = False
#
#import natu.numpy as np
#from natu import units
#from natu.core import ScalarUnit
#
## Semantic overloading: we reuse the "amount" dimension to mean "value"
#
#if config.use_quantities:
#    VND = ScalarUnit(1 / 22270, 'N', 'mol', prefixable=True)
#    units.VND = VND
#
#    USD = ScalarUnit(1, 'N', 'mol', prefixable=True)
#    units.USD = USD
#else:
#    USD = 1
#    VND = USD / 22270
#
#first_year = 2016
#last_year = 2050
#time_horizon = last_year - first_year   # years
#
#v_zeros = np.zeros(time_horizon + 1, dtype=np.float64)
#v_ones = np.ones(time_horizon + 1, dtype=np.float64)
#
#
#def display_as(v, unit):
#    """Sets the display_unit of v or of v's items to 'unit'.
#       Returns v
#       Don't set display_unit directly in the code:
#           it would break when use_quantities = False
#
#    >>> display_as(2 * hr, 's')
#    7200 s
#
#    >>> from natu.units import y
#    >>> v = [48 * hr, 1 * y]
#    >>> v
#    [48 hr, 1 y]
#
#    >>> display_as(v, 'd')
#    [2 d, 365.25 d]
#    """
#    if config.use_quantities:
#        if hasattr(v, '__iter__'):
#            for element in v:
#                element.display_unit = unit
#        else:
#            v.display_unit = unit
#    return v
#
#
#def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
#    """Compare two floats for almost-equality according to PEP 485
#
#    >>> .1 + .1 + .1 == .3
#    False
#
#    >>> isclose(.1 + .1 + .1, .3)
#    True
#    """
#    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
#
#
#def zero_to_NaN(vector):
#    """This zero_to_Nan function:
#    returns a copy of the vector (it's not modified in place), and
#    keeps the unit along
#
#    >>> zero_to_NaN([0, 1, 0 * hr, 'a'])
#    [nan, 1, nan hr, 'a']
#    """
#    return [element if element else element * float('nan') for element in vector]
