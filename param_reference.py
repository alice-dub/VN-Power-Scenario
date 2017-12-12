# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
"""reference is a Parameter  describing the reference technical and economic environment."""

import sys
import numpy as np

from init import pd, show, years, start_year, end_year, n_year, sources
from Parameter import Parameter

from data_OpenEI import (construction_cost, fixed_operating_cost, variable_operating_cost,
                         heat_rate, heat_price)

from data_IPCC import emission_factor

from plan_baseline import plant_life as plant_accounting_life


# %% CCS technologies

start_penalty = 0.30
end_penalty = 0.20
energy_penalty = np.linspace(start_penalty, end_penalty, n_year)
heat_rate["CoalCCS"] = heat_rate["Coal"] * (1 + energy_penalty)
heat_rate["GasCCS"] = heat_rate["Gas"] * (1 + energy_penalty)
heat_rate["BioCCS"] = heat_rate["Biomass"] * (1 + energy_penalty)

show("Heat rate  (Btu/kWh)")
show(heat_rate.round())
show()

heat_price["CoalCCS"] = heat_price["Coal"]
heat_price["GasCCS"] = heat_price["Gas"]
heat_price["BioCCS"] = heat_price["Biomass"]


# %%
"""
Without CCS:
   CO2_emitted = emission_factor_noCCS * production

   CO2_produced = CO2_factor_of_heat * heat_used
   heat_used = production * heat_rate_noCCS
   CO2_produced = CO2_factor_of_heat * production * heat_rate_noCCS

   CO2_produced = CO2_emitted
   CO2_factor_of_heat * production * heat_rate_noCCS = emission_factor_noCCS * production
   CO2_factor_of_heat = emission_factor_noCCS / heat_rate_noCCS

Assume the CO2_factor_of_heat deponds on the fuel only. It is the same with or without CCS.

With CCS:
   CO2_captured = CO2_produced - CO2_emitted

   CO2_emitted = emission_factor_withCCS * production

   CO2_produced = CO2_factor_of_heat * heat_used
   CO2_produced = CO2_factor_of_heat * production * heat_rate_CCS
   CO2_produced = CO2_factor_of_heat * production * heat_rate_noCCS * (1 + energy_penalty)
   CO2_produced = production * emission_factor_noCCS * (1 + energy_penalty)

   CO2_captured = production * capture_factor
   capture_factor = emission_factor_noCCS * (1 + energy_penalty) - emission_factor_withCCS
"""

capture_factor = pd.DataFrame(index=years)
for fuel in sources:
    capture_factor[fuel] = pd.Series(0, index=years)   # gCO2/ kWh

capture_factor["CoalCCS"] = (emission_factor["Coal"] * (1 + energy_penalty)
                             - emission_factor["CoalCCS"])

capture_factor["GasCCS"] = (emission_factor["Gas"] * (1 + energy_penalty)
                            - emission_factor["GasCCS"])

capture_factor["BioCCS"] = (emission_factor["Biomass"] * (1 + energy_penalty)
                            - emission_factor["BioCCS"])

# %%

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


# %%

reference = Parameter(discount_rate,
                      plant_accounting_life,
                      construction_cost[sources],
                      fixed_operating_cost[sources],
                      variable_operating_cost[sources],
                      heat_rate,
                      heat_price,
                      emission_factor,
                      capture_factor,
                      carbon_price)

reference.__doc__ = ("Reference - median values from OpenEI and IPCC reviews, "
                     + "d=" + str(round(100 * discount_rate)) + "%, "
                     + "CO2=" + str(end_carbon_price) + "$ in 2050")

if __name__ == '__main__':
    if (len(sys.argv) == 2) and (sys.argv[1] == "summarize"):
        reference.summarize()
