# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 14:13:45 2018

@author: Alice Duval

Energy unit (for Gas and Coal) is Btu

"""
import sys
from init import pd, start_year, end_year, sources
from plan_baseline import baseline
from param_reference import discount_rate, plant_accounting_life, construction_cost,\
fixed_operating_cost, variable_operating_cost, heat_rate, heat_price,\
emission_factor, capture_factor, carbon_price
from price_fuel import Fuel_Price
from prices_data_local import local_prices
from prices_data_international import international_prices
from production_data_local import local_production
from Run import Run
from Parameter import Parameter

# electric production is in Gwh
electric_production = baseline.production[['Coal', 'Gas']].loc[start_year:end_year+1]

# Heat_rate is in Btu/kWh or in MMBtu/Gwh
useful_heat_rate = heat_rate[['Coal', 'Gas']]

#needed_energy is in MMBtu here

needed_energy = pd.DataFrame(electric_production.values*useful_heat_rate.values,
                             columns=useful_heat_rate.columns, index=useful_heat_rate.index)

#Here: No need to convert: Values are already in MBtu

index = list(range(start_year, end_year+1))

average_price = Fuel_Price(index, local_prices, international_prices, local_production,
                           needed_energy)

updated_heat_price = pd.DataFrame(columns=heat_price.columns, index=heat_price.index)

for fuel in sources:
    if fuel == "Coal" or fuel == "Gas":
        updated_heat_price[fuel] = average_price.average_price[fuel]
    else:
        updated_heat_price[fuel] = heat_price[fuel]

updated_parameter = Parameter(discount_rate,
                      plant_accounting_life,
                      construction_cost[sources],
                      fixed_operating_cost[sources],
                      variable_operating_cost[sources],
                      heat_rate,
                      updated_heat_price,
                      emission_factor,
                      capture_factor,
                      carbon_price)

run_model = Run(baseline, updated_parameter)

if __name__ == '__main__':
    if (len(sys.argv) == 2) and (sys.argv[1] == "summarize"):
        average_price.summarize()
        run_model.summarize()
        print(run_model.string())

    if (len(sys.argv) == 3) and (sys.argv[1] == "plot"):
        average_price.plot_coal_information(sys.argv[2])
        average_price.plot_gas_information(sys.argv[2])
