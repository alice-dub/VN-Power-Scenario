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

ensemble = [reference, hidiscount, lodiscount, hiCarbonPrice, loCoalPrice]

runs = [RunPair(baseline, withCCS, parameter) for parameter in ensemble]

if (len(sys.argv) == 2) and (sys.argv[0] == "analysis.py"):
    if sys.argv[1] == "summarize":
        print("""
******************************************
***       Ensemble of Results          ***
******************************************
""")
        for run in runs:
            print(run.summary(), "\n\n")
    else:
        print('Call this script with "summarize" to print the summary')
