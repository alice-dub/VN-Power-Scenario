# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#
import pandas as pd
#import matplotlib.pyplot as plt
pd.set_option('display.max_rows', 1000)

#
# Read the prepared data
#
# There are common gotchas in energy statistics
#
# 1/ Some sources include imports in electricity "Production"
#    Here we don't and use these column names:
#      Supply = Production + Imports
#
# 2/ Another common ambiguity is whether:
#           "Renewable" includes SmallHydro or not
#           "Hydro" includes SmallHydro or not
#
#    Here we do include SmallHydro in "Hydro" and not in "Renewable"
#    and then use these column names:
#      Hydro = BigHydro + SmallHydro + Pumped storage
#      BigHydro  = LargeHydro + InterHydro
#      Renewable = Wind + Solar + Biomass
#      Renewable4 = Renewable + Small hydro
#
# 3/ Adding up fossil fuel generation capacities with renewable capacities is meaningless
#    because the capacity factors are not comparable, neither are the investment costs
#
# 4/ In VN capacity stats, generation from fuel oil and from diesel is not clearly accounted for
#
# 5/ Pumped storage counts in capacity only, not in production.

#%% Historical capacity addition data

capacity_additions_past = pd.read_fwf("data/capacity_additions_past.txt")

print(capacity_additions_past)

capacity_2015 = capacity_additions_past.groupby(["fuel"]).capacity_MW.sum()
# print("SummaryCapacity in 2015")
# print(capacity_2015)

# Comparision with EVN Annual Report 2016, page 11.
assert capacity_2015.LargeHydro + capacity_2015.InterHydro == 14636
assert capacity_2015.Coal == 12903
assert capacity_2015.Oil == 875
assert capacity_2015.Gas == 7998
assert capacity_2015.Wind == 135
assert capacity_2015.Biofuel + capacity_2015.SmallHydro == 2006

capacity_past = capacity_additions_past.groupby(["year", "fuel"]).capacity_MW.sum()
capacity_past = capacity_past .unstack().fillna(0)
capacity_past.drop("Dummy", axis=1, inplace=True)


def smooth(s):
    """Argument  s  is a numerical series with a numerical value on the last index, 0 elsewhere
       Returns a Pandas series like s, with the value spread linearly
       Values are and remain integers, for example:

       >>> smooth(pd.Series[[0, 0, 0, 10}])
       0    2
       1    2
       2    2
       3    4
       dtype: int64
       """
    n = len(s)
    total = s.iloc[-1]
    annual = int(total // n)
    final = int(total - annual * (n - 1))
    data = [annual] * (n - 1) + [final]
    assert sum(data) == total
    return pd.Series(data, s.index)

#TODO: Find the installation year of intermediate size dams
capacity_past.InterHydro = smooth(capacity_past.InterHydro)
capacity_past.SmallHydro = smooth(capacity_past.SmallHydro)
capacity_past.Oil = smooth(capacity_past.Oil)
capacity_past["Solar"] = 0


#Reorder
capacity_past = capacity_past[["Coal",
                               "Gas",
                               "Oil",
                               "LargeHydro",
                               "InterHydro",
                               "SmallHydro",
                               "Biofuel",
                               "Wind",
                               "Solar"]]

print("""
Vietnam historical capacity additions by fuel type (MW)
Source: Capacities listed in EVN activity report 2016, dated by internet search
""")
print(capacity_past)
print()

print("""
Vietnam historical generation capacity by fuel type (MW)
Source: Capacities listed in EVN activity report 2016, dated by internet search
""")
print(capacity_past.cumsum())
print()

#%%

capacity_past_5cols = capacity_past[["Coal", "Gas", "Oil"]]

capacity_past_5cols["Hydro"] = (capacity_past.LargeHydro
                                + capacity_past.InterHydro
                                + capacity_past.SmallHydro)

capacity_past_5cols["Renewable"] = (capacity_past.Biofuel
                                    + capacity_past.Wind
                                    + capacity_past.Solar)

print("""
Vietnam historical generation capacity by fuel type (MW)
Hydro includes inter and small hydro
Renewable includes biofuel and wind (and solar for zero capacity)
""")
print(capacity_past_5cols.cumsum())
print()


#%%

production_past = pd.read_csv("data/IEA/ElectricityProduction.csv",
                              header=5,
                              index_col=0,
                              usecols=["year", "Coal", "Oil", "Gas", "Biofuels", "Hydro", "Wind"])

production_past['Renewable'] = production_past.Biofuels + production_past.Wind
production_past.drop(["Biofuels", "Wind"], axis=1, inplace=True)


total_production_2015 = 159680   # GWh , EVN 2016 report page 16 and figure p. 20

# Shares by fuel types from Institute of Energy cited in
# http://gizenergy.org.vn/en/knowledge-resources/power-sector-vietnam
# We infer that the 30.0% of Gas includes Oil.
# We infer that the 3.7% of Renewable includes Small hydro.

domestic_supply_2015 = total_production_2015 / 0.985
import_2015 = 0.015 * domestic_supply_2015

coal_2015 = round(0.344 * domestic_supply_2015)

renewable_2015 = 300    # Source: Own estimate, extrapolated from 2014, + Bac Lieu 1 online
hydro_2015 = round((0.304 + 0.037) * domestic_supply_2015) - renewable_2015

oil_2015 = 450         # Source: same as 2015, we have no number about new capacity
gas_2015 = round(0.300 * domestic_supply_2015) - oil_2015

production_2015 = pd.DataFrame({"Coal": {2015: coal_2015},
                                "Gas": {2015: gas_2015},
                                "Hydro": {2015: hydro_2015},
                                "Renewable": {2015: renewable_2015},
                                "Oil": {2015: oil_2015}
                                })

production_past = production_past.append(production_2015)

production_past = production_past[["Coal", "Gas", "Oil", "Hydro", "Renewable"]]

print("""
Vietnam electricity production by fuel type (GWh)
Source IEA 1990-2014, various estimates for 2015
""")
print(production_past)
print()

#%%

capacity_factor_past = production_past / capacity_past_5cols.cumsum() * 1000 / 8760
capacity_factor_past = capacity_factor_past.loc[1990:]

print("""
Vietnam historical capacity factors by fuel type
Source: author
""")
print(capacity_factor_past)

clipped = capacity_factor_past.where((0.1 < capacity_factor_past) & (capacity_factor_past < 1))
clipped.drop("Oil", axis=1).plot(ylim=[0, 1],
                                 xlim=[1995, 2015],
                                 title="Vietnam generation capacity factors by fuel type")

#
#%% Power Development Plan 7 adjusted
#
# Capacity additions
#

PDP7A_annex1 = pd.read_fwf("data/PDP7A/annex1.txt",
                           usecols=["year", "id", "fuel", "capacity_MW"],
                           )

PDP7A_annex1.replace({"fuel": {"TD": "BigHydro",
                               "ND": "Coal",
                               "NDHD": "Oil",
                               "TBKHH": "Gas",
                               "NLTT": "Renewable4",
                               "NMDSK": "Renewable4",  # Biomass
                               "DG": "Renewable4",  # Wind
                               "DMT": "Renewable4",  # Solar
                               "TDN": "Renewable4",  # Small hydro
                               "DHN": "Nuclear",    # Abandonned
                               }},
                     inplace=True
                     )

# print(PDP7A_annex1)

print("""
Summary of 2016-2030 new capacity listed in PDP7A annex 1, MW
Renewable includes Small Hydro
""")
print(PDP7A_annex1.groupby("fuel").capacity_MW.sum())
print("""
*: Backup coal units in case all the renewable sources do not meet the set target (27GW by 2030).
""")

#%%

capacities_PDP7A = pd.read_csv("data/PDP7A/Objectives.csv",
                               header=13,
                               nrows=4,
                               index_col=0)

capacities_PDP7A = capacities_PDP7A.drop(2015)

capacities_PDP7A = capacities_PDP7A[["Coal",
                                     "Gas",
                                     "Hydro",
                                     "BigHydro",
                                     "SmallHydro",
                                     "PumpedStorage",
                                     "Renewable4",
                                     "Renewable",
                                     "Wind",
                                     "Solar",
                                     "Biomass",
                                     "Nuclear"]]

print("""
PDP7A capacity objectives by fuel type (GW)
Renewable includes Small hydro
""")
print(capacities_PDP7A)

#%%

production_PDP7A = pd.read_csv("data/PDP7A/Objectives.csv",
                               header=26,
                               nrows=3,
                               index_col=0,
                               usecols=["year",
                                        "Coal",
                                        "Gas",
                                        "Hydro",
                                        "BigHydro",
                                        "SmallHydro",
                                        "Renewable",
                                        "Nuclear"])

production_PDP7A = production_PDP7A[["Coal",
                                     "Gas",
                                     "Hydro",
                                     "BigHydro",
                                     "SmallHydro",
                                     "Renewable",
                                     "Nuclear"]]

print("""
PDP7A power generation objectives by fuel type (GWh)
""")
print(production_PDP7A)

#%%

capacity_factor_PDP7A = production_PDP7A / capacities_PDP7A * 1000 / 8760

capacity_factor_PDP7A = capacity_factor_PDP7A[["Coal",
                                               "Gas",
                                               "Hydro",
                                               "BigHydro",
                                               "SmallHydro",
                                               "Renewable",
                                               "Nuclear"]]

print("""
Capacity factors implicit in PDP7A decision
based on 8760 hours/year
""")
print(capacity_factor_PDP7A)
