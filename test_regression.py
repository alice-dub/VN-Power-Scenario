# encoding: utf-8
# Economic of co-firing in two power plants in Vietnam
#
# (c) Minh Ha-Duong, An Ha Truong 2016-2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
"""Regression test."""

#import pytest
import numpy as np
from param_reference import reference
from plan_baseline import baseline
from plan_withCCS import withCCS
from prices_data_local import local_prices
from production_data_local import local_production
from Run import RunPair
from prices_data_international import international_prices_path, price_gas, price_coal
from price_fuel import Fuel_Price
from price_LCOE_run import multiple_LCOE
from analysis import RUNPAIRS
# pylint and pytest known compatibility bug
# pylint: disable=redefined-outer-name


def test_reference_str(regtest):
    regtest.write(str(reference))


def test_reference_summary(regtest):
    regtest.write(reference.summary())


def test_withCCS_str(regtest):
    regtest.write(str(withCCS))


def test_withCCS_summary(regtest):
    regtest.write(withCCS.summary())


def test_baseline_str(regtest):
    regtest.write(str(baseline))


def test_baseline_summary(regtest):
    regtest.write(baseline.summary())


def test_runpair_summary(regtest):
    pair = RunPair(baseline, withCCS, reference)
    regtest.write(pair.summary(["Baseline", "High CCS", "difference"]))


def test_analysis(regtest):
    analysis = '\n'.join([runpair.summary(["BAU", "ALT", "difference"]) for runpair in RUNPAIRS])
    regtest.write(analysis)


def test_past_data(regtest):
    international_prices = international_prices_path(price_gas, price_coal)
    regtest.write(international_prices.summary())


def test_fuel_price(regtest):
    np.random.seed(0)
    fuel_prices = Fuel_Price(local_prices, price_gas, price_coal, local_production, baseline)
    regtest.write(fuel_prices.summary())


def test_lcoe_prices(regtest):
    lcoe_list = multiple_LCOE(baseline, 100)
    regtest.write(lcoe_list.summary())
