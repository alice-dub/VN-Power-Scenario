# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#

"""Read the prepared data files corresponding to Vietnam's Power Development Plan 7 Adjusted.

PDP7A groups Oil-fired gas turbines (same technology as aircraft jet engines) with "Gas"

PDP7A list planned fossil fuel plants up to 2030, but does not renewable energy plants after 2022:,
only an total renewable energy capacity.
Solar and wind farms have a relatively short building time, and because the policy is emerging
no land has not been designated yet for these future plants.

PDP7A lists nuclear capacities starting from 2028, but subsequent to its publication
the plans to develop nuclear in Vietnam were scrapped / suspended indefinitely.

PDP7A list of power plant projects include some designated as '* Backup if renewable capacites
are not build.'
"""

from init import pd, show, fuels, Mt, GWh, g, kWh

# %%  List of planned new plants

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

# %% Capacity objectives (Installed GW by fuel type)

capacities_PDP7A = pd.read_csv("data/PDP7A/Objectives.csv", header=13, nrows=4, index_col=0)

capacities_PDP7A = capacities_PDP7A.drop(2015)

capacities_PDP7A["Hydro"] = capacities_PDP7A["Hydro+Storage"] - capacities_PDP7A["PumpedStorage"]
capacities_PDP7A["BigHydro"] = (capacities_PDP7A["BigHydro+Storage"]
                                - capacities_PDP7A["PumpedStorage"])
capacities_PDP7A["Oil"] = 0
capacities_PDP7A["CoalCCS"] = 0
capacities_PDP7A["GasCCS"] = 0
capacities_PDP7A["BioCCS"] = 0

show("""
PDP7A capacity objectives by fuel type (GW)
""")
show(capacities_PDP7A[fuels + ["Nuclear", "Import", "PumpedStorage"]])

# %% Production objectives

production_PDP7A = pd.read_csv("data/PDP7A/Objectives.csv", header=26, nrows=3, index_col=0)

production_PDP7A["Oil"] = 0
production_PDP7A["CoalCCS"] = 0
production_PDP7A["GasCCS"] = 0
production_PDP7A["BioCCS"] = 0

show("""
PDP7A power generation objectives by fuel type (GWh)
""")
show(production_PDP7A[fuels + ["Nuclear", "Import"]])

# %% Implicit capacity factors

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


# %% Coal use objectives mentionned in the PDP (not used in our model)

fuel_use_PDP7A = pd.read_csv("data/PDP7A/Objectives.csv", header=38, nrows=3, index_col=0)

show("Coal consumption, PDP7A (Mt)")
show(fuel_use_PDP7A.Coal)

coal_intensity_PDP7A = (fuel_use_PDP7A.Coal * Mt) / (production_PDP7A.Coal * GWh) / (g / kWh)

show("Coal intensity, PDP7A (g / kWh)")
show(coal_intensity_PDP7A.round())
