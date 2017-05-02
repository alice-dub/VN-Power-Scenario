# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#
import pandas as pd
pd.set_option('display.max_rows', 1000)

PDP7A_annex1 = pd.read_fwf("data/PDP7A/annex1.txt",
                           usecols=["year", "id", "tech", "capacity_MW"],
                           )

PDP7A_annex1.replace({"tech": {"TD": "Hydro",
                               "ND": "Thermal",
                               "TBKHH": "GasCC",
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

print("Total capacity added unded PDP7A, 2016-2030 (MW)")
print(PDP7A_annex1.groupby("tech").capacity_MW.sum())
print()

print("Total capacity added unded PDP7A, 2016-2030 (MW), Nuclear replaced by Thermal")
PDP7A_annex1.replace({"tech": {"Nuclear": "Thermal"}},
                     inplace=True
                     )
print()
# print(PDP7A_annex1.groupby("tech").capacity_MW.sum())
# print()

baseline_capacity_added = PDP7A_annex1.groupby(["year", "tech"]).capacity_MW.sum()
baseline_capacity_added = baseline_capacity_added.unstack().fillna(0)
print("Annual (MW)")
print(baseline_capacity_added)
print()

print("Cumulative since 2016 (MW)")
baseline_capacity_new = baseline_capacity_added.cumsum()
print(baseline_capacity_new)



"""Input parameters of the model"""

discount_rate = {0, 0.05, 0.08, 0.12}
