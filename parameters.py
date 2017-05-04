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


#%% Historical capacity addition data

new_capacity_past = pd.read_fwf("data/new_capacity_past.txt")

# print(new_capacity_past)

capacity_2015 = new_capacity_past.groupby(["fuel"]).capacity_MW.sum()
# print("SummaryCapacity in 2015")
# print(capacity_2015)

# Comparision with EVN Annual Report 2016, page 11.
assert capacity_2015.Hydro == 14636
assert capacity_2015.Coal == 12903
assert capacity_2015.Oil == 875
assert capacity_2015.Gas == 7998
assert capacity_2015.Wind == 135
assert capacity_2015.Biofuel + capacity_2015.SmallHydro == 2006

# TODO: Spread Oil and SmallHydro capacity additions on the 1974 to 2015 intervall

past_capacity_added = new_capacity_past.groupby(["year", "fuel"]).capacity_MW.sum()
past_capacity_added = past_capacity_added .unstack().fillna(0)
past_capacity_added.drop("Dummy", axis=1, inplace=True)

print("Vietnam historical capacity additions by fuel type (MW)")
print(past_capacity_added)
print()

print("Vietnam historical generation capacity by fuel type (MW)")
print(past_capacity_added.cumsum())
print()

#%%

production_past = pd.read_csv("data/IEA/ElectricityProduction.csv",
                              header=5,
                              index_col=0,
                              usecols=["year", "Coal", "Oil", "Gas", "Biofuels", "Hydro", "Wind"])

production_past['Renewable'] = production_past.Biofuels + production_past.Wind
production_past.drop(["Biofuels", "Wind"], axis=1, inplace=True)

#%% 

total_production_2015 = 159680   # GWh , EVN 2016 report page 16 and figure p. 20

# Shares by fuel types from Institute of Energy cited in
# http://gizenergy.org.vn/en/knowledge-resources/power-sector-vietnam
# We infer that the 3.7% of Renewable includes Small hydro.
# We infer that the 30.0% of Gas includes Oil.

domestic_supply_2015 = total_production_2015 / 0.985
import_2015 = 0.015 * domestic_supply_2015

renewable_2015 = 200   # Source: extrapolated from 2014, considering Bac Lieu 1 came online
oil_2015 = 450         # Source: same as 2015, we have no number about new capacity

production_2015 = pd.DataFrame({
                    "Coal": {2015: round(0.344 * domestic_supply_2015)},
                    "Gas": {2015: round(0.300 * domestic_supply_2015) - oil_2015},
                    "Hydro": {2015: round((0.304 + 0.037) * domestic_supply_2015) - renewable_2015},
                    "Renewable": {2015: renewable_2015},
                    "Oil": {2015: oil_2015}
                    })

production_past = production_past.append(production_2015)

print("Vietnam electricity production by fuel type (GWh)\nSource IEA\n")
print(production_past)
print()

#%% Power Development Plan 7 adjusted

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


#%%

#
# define the baseline scenario
#
print("***** Baseline *****")
print()

# The National Assembly voted to cancel the nuclear program
# ASSUMPTION: Planned Nuclear electricity generation capacity is replaced by Coal
baseline = PDP7A_annex1.replace({"tech": {"Nuclear": "Coal"}})

# TODO: update with plants removed from the plan like Bac Lieu
# print(PDP7A_annex1.groupby("tech").capacity_MW.sum())
# print()

baseline_capacity_added = baseline.groupby(["year", "tech"]).capacity_MW.sum()
baseline_capacity_added = baseline_capacity_added.unstack().fillna(0)

# ASSUMPTION: no need for the backup thermal, renewables will be installed as per the plan
baseline_capacity_added.drop("ND*", axis=1, inplace=True)

print("Annual new capacity (MW)")
print(baseline_capacity_added)
print()

print("Cumulative new capacity 2016 (MW)")
print(baseline_capacity_added.cumsum())



"""Input parameters of the model"""

discount_rate = {0, 0.05, 0.08, 0.12}
