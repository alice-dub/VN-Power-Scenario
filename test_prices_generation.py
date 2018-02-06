# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 22:18:16 2018

@author: Alice Duval
"""
from random import randint
import numpy as np

from price_fuel import Fuel_Price
from prices_data_local import local_prices
from plan_baseline import baseline
from prices_data_international import price_gas, price_coal
from production_data_local import local_production
from param_reference import heat_rate
from init import pd, start_year, end_year


def test_international_dependency():
    """Check that if all the production is imported, the average price is equal to the
    international price"""

    # Local production is null
    production = [0] * (end_year+1-start_year)
    nul_production = pd.DataFrame({'Coal': production, 'Gas': production},
    index=range(start_year, end_year+1))

    # Generate random local prices to test the independence of the result
    local_price_gas = []
    local_price_coal = []
    for _ in range(start_year, end_year+1):
        local_price_gas.append(randint(0, 100))
        local_price_coal.append(randint(0, 100))

    local_prices_compare = pd.DataFrame({'Coal': local_price_coal, 'Gas':local_price_gas},
                            index=range(start_year, end_year+1))

    #Create the two objects to compare
    np.random.seed(0)
    fuel_1 = Fuel_Price(local_prices, price_gas, price_coal, nul_production, baseline)
    np.random.seed(0)
    fuel_2 = Fuel_Price(local_prices_compare, price_gas, price_coal, nul_production, baseline)

    assert fuel_1.average_price["Coal"].all() == fuel_2.average_price["Coal"].all()
    assert fuel_1.average_price["Gas"].all() == fuel_2.average_price["Gas"].all()


def test_local_dependency():
    """Check that if all the production is local, the average price is equal to the
    local price"""
    # Local production is equal to energy needs. There is no importation
    electric_production = baseline.production[['Coal', 'Gas']].loc[start_year:end_year+1]
    useful_heat_rate = heat_rate[['Coal', 'Gas']]

    needed_production = pd.DataFrame(electric_production.values*useful_heat_rate.values,
                             columns=useful_heat_rate.columns, index=useful_heat_rate.index)
    # Generate random international prices to test the independence of the result
    past_price_gas = []
    past_price_coal = []
    for _ in range(1970, 2016):
        past_price_coal.append(randint(1, 100))
    for _ in range(1977, 2016):
        past_price_gas.append(randint(1, 100))
    price_gas_compare = pd.DataFrame({'Price_Gas': past_price_gas}, index=range(1977, 2016))
    price_coal_compare = pd.DataFrame({'Price_Coal': past_price_coal}, index=range(1970, 2016))

    #Create the two objects to compare
    np.random.seed(0)
    fuel_1 = Fuel_Price(local_prices, price_gas, price_coal, needed_production, baseline)
    np.random.seed(0)
    fuel_2 = Fuel_Price(local_prices, price_gas_compare, price_coal_compare, needed_production,
                        baseline)
    assert fuel_1.average_price["Gas"].all() == fuel_2.average_price["Gas"].all()
    assert fuel_1.average_price["Coal"].all() == fuel_2.average_price["Coal"].all()

def test_between_two_values():
    """Check that the average price value is between the local value and the international value"""
    fuel_1 = Fuel_Price(local_prices, price_gas, price_coal, local_production, baseline)
    assert pd.concat([fuel_1.international_prices["Gas"], local_prices["Gas"]], axis=1)\
    .min(axis=1).all() <= fuel_1.average_price["Gas"].all()
    assert fuel_1.average_price["Gas"].all() <= pd.concat([fuel_1.international_prices["Gas"],
                               local_prices["Gas"]], axis=1).max(axis=1).all()
