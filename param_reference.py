# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#

import sys

from Parameter import Parameter

from data_OpenEI import (construction_cost, fixed_operating_cost, variable_operating_cost,
                         heat_rate, heat_price)

from data_IPCC import emission_factor

from plan_baseline import plant_life as plant_accounting_life

#%%

discount_rate = 0.05

#%%

reference = Parameter("Reference - median values from OpenEI and IPCC literature reviews",
                      discount_rate,
                      plant_accounting_life,
                      construction_cost,
                      fixed_operating_cost,
                      variable_operating_cost,
                      heat_rate,
                      heat_price,
                      emission_factor)

if (len(sys.argv) == 2) and (sys.argv[0] == "param_reference.py"):
    if sys.argv[1] == "summarize":
        reference.summarize()
    else:
        print('Call this script with "summarize" to print the summary')
