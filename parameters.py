# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#
import pandas as pd
pd.set_option('display.max_rows', 1000)

#
# Read the prepared data
#

PDP7A_annex1 = pd.read_fwf("data/PDP7A/annex1.txt",
                           usecols=["year", "id", "tech", "capacity_MW"],
                           )

PDP7A_annex1.replace({"tech": {"TD": "Hydro",
                               "ND": "Coal",
                               "NDHD": "Oil",
                               "TBKHH": "Gas",
                               "NLTT": "Renewable",
                               "NMDSK": "Renewable",  # Biomass
                               "DG": "Renewable",  # Wind
                               "DMT": "Renewable",  # Solar
                               "TDN": "Renewable",  # Small hydro
                               "DHN": "Nuclear",    # Abandonned
                               }},
                     inplace=True
                     )

# Deal with ND hoa dao is oil not coal

# print(PDP7A_annex1)

print("Summary of 2016-2030 new capacity listed in PDP7A annex 1, MW")
print(PDP7A_annex1.groupby("tech").capacity_MW.sum())
print()

# Source : EVN Annual report 2016, pages 11
capacity_2015 = {"Hydro": 14636, "Coal": 12903, "Oil": 875, "Gas": 7998, "Renewable": 2141}
# TODO: Check that all units listed in PDP7A Annex 1
#  are not in the above table

# TODO: update the PDP using the "investment projects" of the EVN 2016 report

#
# define the baseline scenario
#
print("***** Baseline *****")
print()

# The National Assembly voted to cancel the nuclear program
baseline = PDP7A_annex1.replace({"tech": {"Nuclear": "Coal"}})

# TODO: update with plants removed from the plan like Bac Lieu
# TODO: remove the (*) plants presented as backup if renewable don't fly
# print(PDP7A_annex1.groupby("tech").capacity_MW.sum())
# print()

baseline_capacity_added = baseline.groupby(["year", "tech"]).capacity_MW.sum()
baseline_capacity_added = baseline_capacity_added.unstack().fillna(0)
print("Annual new capacity (MW)")
print(baseline_capacity_added)
print()

print("Cumulative since 2016 (MW)")
baseline_capacity_new = baseline_capacity_added.cumsum()
print(baseline_capacity_new)



"""Input parameters of the model"""

discount_rate = {0, 0.05, 0.08, 0.12}
