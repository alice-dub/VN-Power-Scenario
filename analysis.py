# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#
"""Assess an Ensemble of scenarios."""

import copy
import sys

#from init import timefunc
from init import discountor
from plan_baseline import baseline
from plan_withCCS import withCCS
from param_reference import reference
from Run import RunPair

HIDISCOUNT = copy.deepcopy(reference)
HIDISCOUNT.discount_rate = .08
HIDISCOUNT.docstring = "Discount 8%"

LODISCOUNT = copy.deepcopy(reference)
LODISCOUNT.discount_rate = .04
LODISCOUNT.docstring = "Discount 4%"

HICARBONPRICE = copy.deepcopy(reference)
HICARBONPRICE.carbon_price = reference.carbon_price * 1.75
HICARBONPRICE.docstring = "175% carbon price"

# Coal prices on liberalized markets have been volaile.
# A 100% swing in one year is not exceptionnal
#
# This scenaro's falling 3% per year means division by ~3 from 2016 in 2050
LOCOALPRICE = copy.deepcopy(reference)
LOCOALPRICE.heat_price["Coal"] *= discountor(0.03)
LOCOALPRICE.heat_price["Gas"] *= discountor(0.03)
LOCOALPRICE.docstring = "Coal and Gas price fall by 3% per year"

# Cost decrease in CCS technologies 1% per year (refernce assumes constant costs)
#  -> in 2050 they are 71% of today's cost
# CoalCCS construction costs becomes equal to Coal construction cost in 2039
#
LOCCSCOST = copy.deepcopy(reference)
LOCCSCOST.construction_cost["CoalCCS"] *= discountor(0.018)
LOCCSCOST.fixed_operating_cost["CoalCCS"] *= discountor(0.018)
LOCCSCOST.variable_operating_cost["CoalCCS"] *= discountor(0.018)
LOCCSCOST.construction_cost["GasCCS"] *= discountor(0.018)
LOCCSCOST.fixed_operating_cost["GasCCS"] *= discountor(0.018)
LOCCSCOST.variable_operating_cost["GasCCS"] *= discountor(0.018)
LOCCSCOST.construction_cost["BioCCS"] *= discountor(0.018)
LOCCSCOST.fixed_operating_cost["BioCCS"] *= discountor(0.018)
LOCCSCOST.variable_operating_cost["BioCCS"] *= discountor(0.018)
LOCCSCOST.docstring = "CCS construction and OM costs fall by 1.8% per year"

ENSEMBLE = [reference, HIDISCOUNT, LODISCOUNT, HICARBONPRICE, LOCOALPRICE, LOCCSCOST]

RUNPAIRS = [RunPair(baseline, withCCS, parameter) for parameter in ENSEMBLE]


if __name__ == '__main__':
    if (len(sys.argv) == 2) and (sys.argv[1] == "summarize"):
        print("""
******************************************
***       Ensemble of Results          ***
******************************************
""")
        for runpair in RUNPAIRS:
            print(runpair.summary(["BAU", "ALT", "difference"]), "\n\n")


#@timefunc
#def speedtest():
#    for runpair in RUNPAIRS:
#        runpair.summary(["BAU", "ALT", "difference"])
#
#print()
#speedtest()
