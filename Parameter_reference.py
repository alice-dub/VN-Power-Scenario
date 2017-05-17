# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#

from init import pd, sources

from data_OpenEI import (construction_cost, fixed_operating_cost, variable_operating_cost,
                         heat_rate, heat_price)

from PowerPlan_baseline import plant_life as plant_accounting_life


class Parameter():

    def __init__(self,
                 docstring,
                 discount_rate,
                 plant_accounting_life,
                 construction_cost,
                 fixed_operating_cost,
                 variable_operating_cost,
                 heat_rate,
                 heat_price,
                 emission_factor):
        self.docstring = docstring
        self.discount_rate = discount_rate
        self.plant_accounting_life = plant_accounting_life
        self.construction_cost = construction_cost[sources]
        self.fixed_operating_cost = fixed_operating_cost[sources]
        self.variable_operating_cost = variable_operating_cost[sources]
        self.heat_rate = heat_rate
        self.heat_price = heat_price
        self.emission_factor = emission_factor

    def __str__(self):
        return ("Parameters: " + self.docstring)

    def summarize(self):
        print(self)
        print()
        summary = pd.DataFrame()
        s = self.plant_accounting_life[sources]
        s.name = "Plant accounting life (year)"
        summary = summary.append(s)
        s = self.emission_factor[sources]
        s.name = "Emission factor (gCO2eq/kWh)"
        summary = summary.append(s)
        s = self.construction_cost.round().loc[2016]
        s.name = "Overnight construction costs ($/kW)"
        summary = summary.append(s)
        s = (self.construction_cost.loc[2017] - self.construction_cost.loc[2016]).round(2)
        s.name = "Overnight construction costs trend ($/kW/y)"
        summary = summary.append(s)
        s = self.fixed_operating_cost.round(2).loc[2016]
        s.name = "Fixed operating costs ($/kW)"
        summary = summary.append(s)
        s = (self.fixed_operating_cost.loc[2017] - self.fixed_operating_cost.loc[2016]).round(2)
        s.name = "Fixed operating costs trend ($/kW/yr)"
        summary = summary.append(s)
        s = self.variable_operating_cost.round(2).loc[2016]
        s.name = "Variable operating costs ($/kWh)"
        summary = summary.append(s)
        s = self.heat_rate.loc[2016]
        s.name = "Heat rate (Btu/kWh)"
        summary = summary.append(s)
        s = self.heat_price.loc[2016]
        s.name = "Heat price ($/MBtu)"
        summary = summary.append(s)
        print(summary[sources])
        print()
        print("Discount rate:", self.discount_rate)

    def detail(self):
        print(self)
        print()
        print("Discount rate:", self.discount_rate)
        print()
        print("Plant accounting life (year)")
        print(self.plant_accounting_life[sources])
        print()
        print("Emission factor (gCO2eq/kWh)")
        print(self.emission_factor[sources])
        print()
        print("Overnight construction costs ($/kW)")
        print(self.construction_cost.round())
        print()
        print("Fixed operating costs ($/kW)")
        print(self.fixed_operating_cost.round(2))
        print()
        print("Variable operating costs ($/kWh)")
        print(self.variable_operating_cost.round(2))
        print()
        print("Heat rate (Btu/kWh)")
        print(self.heat_rate)
        print()
        print("Heat price ($/MBtu)")
        print(self.heat_price)
        print()


#%% Emission factors

#Source : IPCC SRREN
# Table A.II.4 | Aggregated results of literature review of LCAs of GHG emissions
# from electricity generation technologies (g CO2eq/kWh)
# Median of the literature reviewed

emission_factor = pd.Series({"Coal": 1001, "Gas": 469, "Oil": 840, "BigHydro": 4,
                             "SmallHydro": 4, "Biomass": 18, "Wind": 12, "Solar": 46,
                             "Coal CCS": float('NaN'), "Gas CCS": float('NaN'),
                             "Biomass CCS": float('NaN')})

#Assumption: VN imports from China and Lao
emission_factor["Import"] = 0.5 * emission_factor["Coal"] + 0.5 * emission_factor["BigHydro"]

#%%

discount_rate = 0.05


#%%   economic life, to assess residual value by linear depreciation
#
#plant_accounting_life = plant_life

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

# reference.detail()
print("""
******************************************
***             Parameters             ***
******************************************
""")

reference.summarize()
