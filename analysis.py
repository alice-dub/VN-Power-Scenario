# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#


"""
Assess an ensemble of scenarios

"""

import copy
import sys

from init import discountor
from plan_baseline import baseline
from plan_withCCS import withCCS
from param_reference import reference
from Run import RunPair

hidiscount = copy.deepcopy(reference)
hidiscount.discount_rate = .08
hidiscount.docstring = "Discount 8%"

lodiscount = copy.deepcopy(reference)
lodiscount.discount_rate = .04
lodiscount.docstring = "Discount 4%"

hiCarbonPrice = copy.deepcopy(reference)
hiCarbonPrice.carbon_price = reference.carbon_price * 1.75
hiCarbonPrice.docstring = "175% carbon price"

# Coal prices on liberalized markets have been volaile.
# A 100% swing in one year is not exceptionnal
#
# This scenaro's falling 3% per year means division by ~3 from 2016 in 2050
loCoalPrice = copy.deepcopy(reference)
loCoalPrice.heat_price["Coal"] *= discountor(0.03)
loCoalPrice.heat_price["Gas"] *= discountor(0.03)
loCoalPrice.docstring = "Coal and Gas price fall by 3% per year"

# Cost decrease in CCS technologies 1% per year (refernce assumes constant costs)
#  -> in 2050 they are 71% of today's cost
# CoalCCS construction costs becomes equal to Coal construction cost in 2039
#
loCCSCost = copy.deepcopy(reference)
loCCSCost.construction_cost["CoalCCS"] *= discountor(0.018)
loCCSCost.fixed_operating_cost["CoalCCS"] *= discountor(0.018)
loCCSCost.variable_operating_cost["CoalCCS"] *= discountor(0.018)
loCCSCost.construction_cost["GasCCS"] *= discountor(0.018)
loCCSCost.fixed_operating_cost["GasCCS"] *= discountor(0.018)
loCCSCost.variable_operating_cost["GasCCS"] *= discountor(0.018)
loCCSCost.construction_cost["BioCCS"] *= discountor(0.018)
loCCSCost.fixed_operating_cost["BioCCS"] *= discountor(0.018)
loCCSCost.variable_operating_cost["BioCCS"] *= discountor(0.018)
loCCSCost.docstring = "CCS construction and OM costs fall by 1.8% per year"

ensemble = [reference, hidiscount, lodiscount, hiCarbonPrice, loCoalPrice, loCCSCost]

runs = [RunPair(baseline, withCCS, parameter) for parameter in ensemble]

if (len(sys.argv) == 2) and (sys.argv[0] == "analysis.py"):
    if sys.argv[1] == "summarize":
        print("""
******************************************
***       Ensemble of Results          ***
******************************************
""")
        for run in runs:
            print(run.summary(["BAU", "ALT", "difference"]), "\n\n")
    else:
        print('Call this script with "summarize" to print the summary')
