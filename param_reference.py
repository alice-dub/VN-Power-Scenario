# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#

import sys
import numpy as np

from init import pd, years, start_year, end_year
from Parameter import Parameter

from data_OpenEI import (construction_cost, fixed_operating_cost, variable_operating_cost,
                         heat_rate, heat_price)

from data_IPCC import emission_factor

from plan_baseline import plant_life as plant_accounting_life

#%%

discount_rate = 0.06

start_carbon_price = 0
mid1_year = 2020
mid1_carbon_price = 0
mid2_year = 2030
mid2_carbon_price = 50
end_carbon_price = 100

carbon_price = np.concatenate([np.linspace(start_carbon_price,
                                           mid1_carbon_price,
                                           mid1_year - start_year,
                                           endpoint=False),
                               np.linspace(mid1_carbon_price,
                                           mid2_carbon_price,
                                           mid2_year - mid1_year,
                                           endpoint=False),
                               np.linspace(mid2_carbon_price,
                                           end_carbon_price,
                                           end_year - mid2_year + 1)])

carbon_price = pd.Series(data=carbon_price, index=years)


#%%

reference = Parameter(("Reference - median values from OpenEI and IPCC reviews, "
                       + "d=" + str(round(100 * discount_rate)) + "%, "
                       + "CO2=" + str(end_carbon_price) + "$ in 2050"),
                      discount_rate,
                      plant_accounting_life,
                      construction_cost,
                      fixed_operating_cost,
                      variable_operating_cost,
                      heat_rate,
                      heat_price,
                      emission_factor,
                      carbon_price)

if (len(sys.argv) == 2) and (sys.argv[0] == "param_reference.py"):
    if sys.argv[1] == "summarize":
        reference.summarize()
    else:
        print('Call this script with "summarize" to print the summary')
