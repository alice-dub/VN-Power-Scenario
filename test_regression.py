# encoding: utf-8
# Economic of co-firing in two power plants in Vietnam
#
# (c) Minh Ha-Duong, An Ha Truong 2016-2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
"""Regression test."""

#import pytest

from param_reference import reference
from plan_baseline import baseline
from plan_withCCS import withCCS
from Run import RunPair
# pylint and pytest known compatibility bug
# pylint: disable=redefined-outer-name


def test_reference_str(regtest):
    regtest.write(str(reference))


def test_reference_summary(regtest):
    regtest.write(reference.summary())


def test_reference_string(regtest):
    regtest.write(reference.string())


def test_withCCS_str(regtest):
    regtest.write(str(withCCS))


def test_withCCS_summary(regtest):
    regtest.write(withCCS.summary())


def test_withCCS_string(regtest):
    regtest.write(withCCS.string())


def test_baseline_str(regtest):
    regtest.write(str(baseline))


def test_baseline_summary(regtest):
    regtest.write(baseline.summary())


def test_baseline_string(regtest):
    regtest.write(baseline.string())


def test_runpair_summary(regtest):
    pair = RunPair(baseline, withCCS, reference)
    regtest.write(pair.summary(["Baseline", "High CCS", "difference"]))
