# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#

import pandas as pd

from init import sources

from data_baseline import plant_life

from data_OpenEI import (construction_cost, fixed_operating_cost, variable_operating_cost,
                         heat_rate, heat_price)


class Parameter():

    def __init__(self,
                 discount_rate,
                 plant_accounting_life,
                 construction_cost,
                 fixed_operating_cost,
                 variable_operating_cost,
                 heat_rate,
                 heat_price,
                 emission_factor):
        self.discount_rate = discount_rate
        self.plant_accounting_life = plant_accounting_life
        self.construction_cost = construction_cost[sources]
        self.fixed_operating_cost = fixed_operating_cost[sources]
        self.variable_operating_cost = variable_operating_cost[sources]
        self.heat_rate = heat_rate
        self.heat_price = heat_price
        self.emission_factor = emission_factor

    def __str__(self):
        return ("Parameters set #" + str(hash(self)))

    def summarize(self):
        print("Discount rate:", self.discount_rate)
        #TODO: Print a summary table

    def detail(self):
        print("Discount rate:", self.discount_rate)
        print("Overnight construction costs ($/kW)")
        print(self.construction_cost.round())
        print()
        print("Fixed operating costs ($/kW)")
        print(self.fixed_operating_cost)
        print()
        print("Variable operating costs ($/kWh)")
        print(self.variable_operating_cost)
        print()
        print("Heat rate (Btu/kWh)")
        print(self.heat_rate)
        print()
        print("Heat price ($/MBtu)")
        print(self.heat_price)
        print()
        print("Emission factor (gCO2eq/kWh)")
        print(self.emission_factor)
        print()


#%% Emission factors

#Source : IPCC SRREN
# Table A.II.4 | Aggregated results of literature review of LCAs of GHG emissions
# from electricity generation technologies (g CO2eq/kWh)
# Median of the literature reviewed

emission_factor = pd.Series({"Coal": 1001, "Gas": 469, "Oil": 840, "BigHydro": 4,
                             "SmallHydro": 4, "Biomass": 18, "Wind": 12, "Solar": 46})

#Assumption: VN imports from China and Lao
emission_factor["Import"] = 0.5 * emission_factor["Coal"] + 0.5 * emission_factor["BigHydro"]

#%%

discount_rate = 0.05

#%%   economic life, to assess residual value by linear depreciation

plant_accounting_life = plant_life

#%%

reference = Parameter(discount_rate,
                      plant_accounting_life,
                      construction_cost,
                      fixed_operating_cost,
                      variable_operating_cost,
                      heat_rate,
                      heat_price,
                      emission_factor)
