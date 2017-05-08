# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#

"""
Read the prepared data files

There are 3 data sources (PDP7A, EVN 2016 report, IEA statistics)
so we need to clarify column names.

 1/ Some include Imports in electricity "Production"
    Here we don't --it's clearly wrong-- and use these column names:
      Supply = Production + Imports

 2/ Another ambiguity is whether SmallHydro is included in "Hydro" or "Renewable"
    Here we do the former and use these column names:
      Hydro = BigHydro + SmallHydro
      BigHydro = LargeHydro + InterHydro
      Renewable = Wind + Solar + Biomass
      Renewable4 = Renewable + Small hydro

 3/ We do NOT include PumpedStorage in Hydro capacities

 4/ Adding up fossil fuel generation capacities with renewable capacities is meaningless
    because the capacity factors are not comparable, neither are the investment costs

 5/ In VN capacity stats, generation from fuel oil and from diesel is not clearly accounted for
"""

import pandas as pd
#import matplotlib.pyplot as plt
pd.set_option('display.max_rows', 1000)

#%% Historical capacity addition data

capacity_additions_past = pd.read_fwf("data/capacity_additions_past.txt")

print(capacity_additions_past)

capacity_2015_EVN = capacity_additions_past.groupby(["fuel"]).capacity_MW.sum()
# print("SummaryCapacity in 2015")
# print(capacity_2015)

# Comparision with EVN Annual Report 2016, page 11.
capacity_2015_EVN["BigHydro"] = capacity_2015_EVN.LargeHydro + capacity_2015_EVN.InterHydro
assert capacity_2015_EVN.BigHydro == 14636
assert capacity_2015_EVN.Coal == 12903
assert capacity_2015_EVN.Oil == 875
assert capacity_2015_EVN.Gas == 7998
assert capacity_2015_EVN.Wind == 135
assert capacity_2015_EVN.Biomass + capacity_2015_EVN.SmallHydro == 2006
capacity_2015_EVN["Renewable4"] = (capacity_2015_EVN.SmallHydro
                                   + capacity_2015_EVN.Wind
                                   + capacity_2015_EVN.Biomass)


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


#Reorder
capacity_past = capacity_past[["Coal",
                               "Gas",
                               "Oil",
                               "LargeHydro",
                               "InterHydro",
                               "SmallHydro",
                               "Biomass",
                               "Wind"]]

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

capacity_past_5cols["BigHydro"] = (capacity_past.LargeHydro
                                   + capacity_past.InterHydro)

capacity_past_5cols["Renewable4"] = (capacity_past.SmallHydro
                                     + capacity_past.Biomass
                                     + capacity_past.Wind)
#                                    + There was no solar in past

print("""
Vietnam historical generation capacity by fuel type (MW)
Small hydro included in Renewable4
(historically, no Solar or Pumped Storage)
""")
print(capacity_past_5cols.cumsum())
print()

capacity_past_IEAcols = capacity_past[["Coal", "Gas", "Oil"]]

capacity_past_IEAcols["Hydro"] = (capacity_past.LargeHydro
                                  + capacity_past.InterHydro
                                  + capacity_past.SmallHydro)

capacity_past_IEAcols["Renewable"] = (capacity_past.Biomass
                                      + capacity_past.Wind)


print("""
Vietnam historical generation capacity by fuel type (MW)
Small hydro included in Hydro
""")
print(capacity_past_IEAcols.cumsum())
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

capacity_factor_past = production_past / capacity_past_IEAcols.cumsum() * 1000 / 8760
capacity_factor_past = capacity_factor_past.loc[1990:]

print("""
Vietnam historical capacity factors by fuel type
Source: author
""")
print(capacity_factor_past)

#
#%% Power Development Plan 7 adjusted
#
# Capacity additions
#

PDP7A_annex1 = pd.read_fwf("data/PDP7A/annex1.txt",
                           usecols=["year", "id", "fuel", "capacity_MW"],
                           )

PDP7A_annex1.replace({"fuel": {"ND": "Coal",
                               "NDHD": "Oil",
                               "TBKHH": "Gas",
                               "TD": "BigHydro",
                               "TDTN": "PumpedStorage",
                               "NLTT": "Renewable4",   # Renewable energy (agregate)
                               "TDN": "Renewable4",    # Small hydro
                               "NMDSK": "Renewable4",  # Biomass
                               "DG": "Renewable4",     # Wind
                               "DMT": "Renewable4",    # Solar
                               "DHN": "Nuclear",
                               }},
                     inplace=True
                     )

# print(PDP7A_annex1)

capacity_total_plan = PDP7A_annex1.groupby("fuel").capacity_MW.sum()
print("""
Summary of 2016-2030 new capacity listed in PDP7A annex 1, MW
Renewable4 includes Small Hydro
""")
print(capacity_total_plan)
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
                                     "Hydro+Storage",
                                     "BigHydro+Storage",
                                     "SmallHydro",
                                     "PumpedStorage",
                                     "Renewable4",
                                     "Renewable",
                                     "Wind",
                                     "Solar",
                                     "Biomass",
                                     "Nuclear"]]

capacities_PDP7A["Hydro"] = capacities_PDP7A["Hydro+Storage"] - capacities_PDP7A["PumpedStorage"]
capacities_PDP7A["BigHydro"] = (capacities_PDP7A["BigHydro+Storage"]
                                - capacities_PDP7A["PumpedStorage"])

print("""
PDP7A capacity objectives by fuel type (GW)
""")
print(capacities_PDP7A)

#%%

cap_2015_implicit = capacities_PDP7A.loc[2030] - capacity_total_plan

cap_2015_implicit.dropna(inplace=True)

comparison = pd.DataFrame([capacity_2015_EVN, cap_2015_implicit],
                          index=["Total from EVN report", "Implicit in PDP7A decision"])

capacity_closed = pd.Series(comparison.iloc[0] - comparison.iloc[1], name="Diff ?Closed capacity?")

comparison = comparison.append(capacity_closed)

capacity_old = pd.Series(capacity_past_5cols.cumsum().loc[1980], name="Installed before 1980")

comparison = comparison.append(capacity_old)

comparison = comparison[["Coal",
                         "Gas",
                         "BigHydro",
                         "SmallHydro",
                         "PumpedStorage",
                         "Renewable4",
                         "Oil",
                         "Wind",
                         "Biomass",
                         "Nuclear"]]

print("Coherence of 2015 Generation capacity numbers")
print(comparison)

print("""
Some coal, gas, oil and hydro capacities listed in the EVN report historical table are
not accounted for in the PDP7A current capacity total
The order of magnitude corresponds to capacities installed before 1985,
which in all probability are already closed or will be before 2030.
#TODO: Check the operational status of these plants:

Gas capacity in EVN report includes the Tu Duc and Can Tho oil-fired gas turbines (264 MW)
""")

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

cf = pd.concat([capacity_factor_past, capacity_factor_PDP7A])
cf = cf.where(cf < 1)
cf = cf[["Coal", "Gas", "Hydro", "Renewable"]]
ax = cf.plot(ylim=[0, 1], xlim=[1995, 2030], title="Power generation capacity factors by fuel type")
ax.axvline(2015, color="k")
