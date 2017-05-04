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


# print(PDP7A_annex1)

print("Summary of 2016-2030 new capacity listed in PDP7A annex 1, MW")
print(PDP7A_annex1.groupby("tech").capacity_MW.sum())
print("""
ND*: Backup coal units in case all the renewable sources do not meet the set target (27GW by 2030).
""")

new_capacity_past = pd.read_fwf("data/new_capacity_past.txt")

# print(new_capacity_past)

capacity_2015 = new_capacity_past.groupby(["tech"]).capacity_MW.sum()
print("Capacity in 2015")
print(capacity_2015)

# Comparision with EVN Annual Report 2016, page 11.
assert capacity_2015.Hydro == 14636
assert capacity_2015.Coal == 12903
assert capacity_2015.Oil == 875
assert capacity_2015.Gas == 7998
assert capacity_2015.Renewable == 2006 + 135

# TODO: Spread Oil and Renewable capacity additions on the 1974 to 2015 intervall

past_capacity_added = new_capacity_past.groupby(["year", "tech"]).capacity_MW.sum()
past_capacity_added = past_capacity_added .unstack().fillna(0)
print(past_capacity_added)

#
# define the baseline scenario
#
print("***** Baseline *****")
print()

# The National Assembly voted to cancel the nuclear program
# ASSUMPTION: Planned Nuclear electricity generation capacity is replaced by Coal
baseline = PDP7A_annex1.replace({"tech": {"Nuclear": "Coal"}})

# TODO: Drop TD*
# TODO: remove the (*) plants presented as backup if renewable don't fly

# TODO: update with plants removed from the plan like Bac Lieu
# print(PDP7A_annex1.groupby("tech").capacity_MW.sum())
# print()

baseline_capacity_added = baseline.groupby(["year", "tech"]).capacity_MW.sum()
baseline_capacity_added = baseline_capacity_added.unstack().fillna(0)
print("Annual new capacity (MW)")
print(baseline_capacity_added)
print()

print("Cumulative new capacity 2016 (MW)")
print(baseline_capacity_added.cumsum())



"""Input parameters of the model"""

discount_rate = {0, 0.05, 0.08, 0.12}
