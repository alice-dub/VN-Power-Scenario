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

 4/ We define Import as net of Exports

 5/ In VN capacity stats, generation from fuel oil and from diesel is not clearly accounted for

 6/ Adding up fossil fuel generation capacities with renewable capacities is meaningless
    because the capacity factors are not comparable, neither are the investment costs
"""

import pandas as pd
from init import show, VERBOSE, fuels, sources

pd.set_option('display.max_rows', 100)


def addcol_Renewable(s):
    s["Renewable"] = s["Biomass"] + s["Wind"] + s["Solar"]


def addcol_Renewable4(s):
    s["Renewable4"] = s["Biomass"] + s["Wind"] + s["Solar"] + s["SmallHydro"]


#%% Read data from EVN 2016 activity report
# Historical capacity addition

capacity_additions_past = pd.read_fwf("data/capacity_additions_past.txt")

show(capacity_additions_past)

capacity_2015_EVN = capacity_additions_past.groupby(["fuel"]).capacity_MW.sum()
# show("SummaryCapacity in 2015")
# show(capacity_2015)

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

capacity_past["Solar"] = 0
capacity_past["Import"] = 0
capacity_past["PumpedStorage"] = 0

capacity_past["BigHydro"] = (capacity_past.LargeHydro
                             + capacity_past.InterHydro)

capacity_past["Hydro"] = (capacity_past.BigHydro
                          + capacity_past.SmallHydro)

addcol_Renewable(capacity_past)
addcol_Renewable4(capacity_past)

show("""
Vietnam historical capacity additions by fuel type (MW)
Source: Capacities listed in EVN activity report 2016, dated by internet search
""")
show(capacity_past[fuels])
show()

show("""
Vietnam historical generation capacity by fuel type (MW)
Source: Capacities listed in EVN activity report 2016, dated by internet search
""")
show(capacity_past[fuels].cumsum())
show()

show("""
Vietnam historical generation capacity by fuel type (MW)
Small hydro included in Renewable4
""")

show(capacity_past[["Coal", "Gas", "Oil", "BigHydro", "Renewable4"]].cumsum())
show()

show("""
Vietnam historical generation capacity by fuel type (MW)
Small hydro included in Hydro
""")
show(capacity_past[["Coal", "Gas", "Oil", "Hydro", "Renewable"]].cumsum())
show()


#%% read data from International Energy Agency

production_past = pd.read_csv("data/IEA/ElectricityProduction.csv", header=5, index_col=0)

production_past["Solar"] = 0
addcol_Renewable(production_past)
production_past["SmallHydro"] = (production_past.Hydro *
                                 capacity_past.SmallHydro / capacity_past.Hydro)
production_past["SmallHydro"] = production_past["SmallHydro"].astype(int)
production_past["BigHydro"] = production_past.Hydro - production_past.SmallHydro
production_past["Import"] = production_past.Imports + production_past.Exports

#%% Estimates 2015 production by fuel type
# Source Institute of Energy cited in
# http://gizenergy.org.vn/en/knowledge-resources/power-sector-vietnam
"""The annual electricity production increased to 164.31 TWh in 2015.
In 2015, coal accounted for the largest share of electricity production (34.4%),
followed by hydropower (30.4%) and gas (30%). Apart from large-scale hydropower,
renewable energy - including small-scale hydropower - represented only a minor part
of the electricity production (3.7%).
The figure adds that: Imports represented 1.5%, we infer that the production number is the total
domestic supply. The Gas cheese slice label is "Gas Turbine" which includes Oil fueled gas turbines.
"""
# This implies a total production of 164310 * 0.985 = 161.8 TWh
# which compares to  159.7 TWh given in EVN 2016 report page 16

domestic_supply_2015 = 164310  # GWh

production_2015 = pd.Series(name=2015,
                            data={"Coal": round(0.344 * domestic_supply_2015),
                                  "BigHydro": round(0.304 * domestic_supply_2015),
                                  "GasTurbine": round(0.300 * domestic_supply_2015),
                                  "Renewable4": round(0.037 * domestic_supply_2015),
                                  "Import": round(0.015 * domestic_supply_2015)})

production_2015["Oil"] = 450  # Source: Own estimate, same as 2015, we have no idea
production_2015["Gas"] = production_2015["GasTurbine"] - production_2015["Oil"]
production_2015["Wind"] = 240         # Source: Own estimate, 2014 + Bac Lieu 1 online
production_2015["Biomass"] = 60       # Continuity with 2014 level and trend
production_2015["Solar"] = 0          # Commercial solar power not allowed by law yet
addcol_Renewable(production_2015)
production_2015["SmallHydro"] = production_2015["Renewable4"] - production_2015["Renewable"]
production_2015["Hydro"] = production_2015["BigHydro"] + production_2015["SmallHydro"]

production_2015.drop(["GasTurbine", "Renewable4"], inplace=True)

production_past = production_past.append(production_2015)

show("""
Vietnam electricity production by fuel type (GWh)
Source IEA 1990-2014
Source GiZ citing Institute of Energy for 2015
Hydro production divided between small and big proportional to capacity
Imports are net of exports
""")
show(production_past[sources])
show()

#%%

capacity_factor_past = production_past / capacity_past.cumsum() * 1000 / 8760
capacity_factor_past = capacity_factor_past.loc[1990:]

show("""
Vietnam historical capacity factors by fuel type
Source: author
""")
show(capacity_factor_past[fuels].drop("Solar", axis=1))

#
#%% Power Development Plan 7 adjusted
#
# Capacity additions
#

PDP7A_annex1 = pd.read_fwf("data/PDP7A/annex1.txt")

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

# show(PDP7A_annex1)

capacity_total_plan = PDP7A_annex1.groupby("fuel").capacity_MW.sum()
show("""
Summary of 2016-2030 new capacity listed in PDP7A annex 1, MW
""")
show(capacity_total_plan)
show("""
*: Backup coal units in case all the renewable sources do not meet the set target (27GW by 2030).
Small hydro not specified, included in Renewable4
Wind, Solar, Biomass not specifed after 2020
""")

#%%

capacities_PDP7A = pd.read_csv("data/PDP7A/Objectives.csv", header=13, nrows=4, index_col=0)

capacities_PDP7A = capacities_PDP7A.drop(2015)

capacities_PDP7A["Hydro"] = capacities_PDP7A["Hydro+Storage"] - capacities_PDP7A["PumpedStorage"]
capacities_PDP7A["BigHydro"] = (capacities_PDP7A["BigHydro+Storage"]
                                - capacities_PDP7A["PumpedStorage"])
capacities_PDP7A["Oil"] = 0

show("""
PDP7A capacity objectives by fuel type (GW)
""")
show(capacities_PDP7A[fuels + ["Nuclear", "Import", "PumpedStorage"]])

#%%

cap_2015_implicit = capacities_PDP7A.loc[2030] - capacity_total_plan

cap_2015_implicit.dropna(inplace=True)

comparison = pd.DataFrame([capacity_2015_EVN, cap_2015_implicit],
                          index=["Total from EVN report", "Implicit in PDP7A decision"])

capacity_closed = pd.Series(comparison.iloc[0] - comparison.iloc[1], name="Diff ?Closed capacity?")

comparison = comparison.append(capacity_closed)

capacity_old = pd.Series(capacity_past.cumsum().loc[1980], name="Installed before 1980")

comparison = comparison.append(capacity_old)

show("Coherence of 2015 Generation capacity numbers")
show(comparison[fuels])

show("""
Some coal, gas, oil and hydro capacities listed in the EVN report historical table are
not accounted for in the PDP7A current capacity total
The order of magnitude corresponds to capacities installed before 1985,
which in all probability are already closed or will be before 2030.
#TODO: Check the operational status of these plants:

Gas capacity in EVN report includes the Tu Duc and Can Tho oil-fired gas turbines (264 MW)
""")

#%%

production_PDP7A = pd.read_csv("data/PDP7A/Objectives.csv", header=26, nrows=3, index_col=0)

production_PDP7A["Oil"] = 0

show("""
PDP7A power generation objectives by fuel type (GWh)
""")
show(production_PDP7A[fuels + ["Nuclear", "Import"]])

#%%

capacity_factor_PDP7A = production_PDP7A / capacities_PDP7A * 1000 / 8760

capacity_factor_PDP7A = capacity_factor_PDP7A[["Coal",
                                               "Gas",
                                               "Hydro",
                                               "BigHydro",
                                               "SmallHydro",
                                               "Renewable",
                                               "Nuclear"]]

show("""
Capacity factors implicit in PDP7A decision
based on 8760 hours/year
""")
show(capacity_factor_PDP7A)

if VERBOSE:
    cf = pd.concat([capacity_factor_past, capacity_factor_PDP7A])
    cf = cf.where(cf < 1)
    cf = cf[["Coal", "Gas", "Hydro", "Renewable"]]
    ax = cf.plot(ylim=[0, 1], xlim=[1995, 2030],
                 title="Power generation capacity factors by fuel type")
    ax.axvline(2015, color="k")


#%%

fuel_use_PDP7A = pd.read_csv("data/PDP7A/Objectives.csv", header=38, nrows=3, index_col=0)

show("Coal consumption, PDP7A (Mt)")
show(fuel_use_PDP7A.Coal)

#%%  Plant physical life - when to retire from production capacities

plant_life = pd.Series({"Coal": 40, "Gas": 25, "Oil": 30, "BigHydro": 100,
                        "SmallHydro": 60, "Biomass": 25, "Wind": 20, "Solar": 25,
                        "PumpedStorage": 100, "Import": 100})
