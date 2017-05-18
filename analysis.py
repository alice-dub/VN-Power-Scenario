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

ensemble = [reference, hidiscount, lodiscount, hiCarbonPrice]

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

