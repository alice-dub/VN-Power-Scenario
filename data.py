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
# There are common gotchas in energy statistics
#
# 1/ Domestic supply = Production + Imports,
#    but in some sources the label "Production" means "Supply"
#
# 2/ Hydro = Large Hydro + Medium Hydro + Small Hydro
#    Renewables = Small hydro + Wind + Solar + Biomass
#    so there are two ways to define "Hydro" and "Renewable", depending on where Small Hydro is
#    Before other Renewables mattered, the choice was obvious
#
# 3/ Adding up fossil fuel generation capacities with renewable capacities is meaningless
#    because the capacity factors are not comparable, neither are the investment costs
#
# 4/ "Others" also includes Small Diesel commercial power.
#
# 5/ Fuel Oil generation accounted with "Gas" I think because minor share and also use gas turbines

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

past_capacity_added = new_capacity_past.groupby(["year", "fuel"]).capacity_MW.sum()
past_capacity_added = past_capacity_added .unstack().fillna(0)
past_capacity_added.drop("Dummy", axis=1, inplace=True)


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

past_capacity_added.SmallHydro = smooth(past_capacity_added.SmallHydro)
past_capacity_added.Oil = smooth(past_capacity_added.Oil)


#%%

print("""
Vietnam historical capacity additions by fuel type (MW)
Source: Capacities listed in EVN activity report 2016, dated by internet search
""")
print(past_capacity_added)
print()

print("""
Vietnam historical generation capacity by fuel type (MW)
Source: Capacities listed in EVN activity report 2016, dated by internet search
""")
print(past_capacity_added.cumsum())
print()

#%%

past_capacity_added["Renewable"] = (past_capacity_added.Biofuel
                                    + past_capacity_added.SmallHydro
                                    + past_capacity_added.Wind)

simpler_past_capacity = past_capacity_added.drop(["Biofuel", "SmallHydro", "Wind"], axis=1)

print("""
Vietnam historical generation capacity by fuel type (MW)
Renewable includes small hydro, biofuel, wind (there is no solar capacity)
""")
print(simpler_past_capacity.cumsum())
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
# We infer that the 30.0% of Gas includes Oil.
# We infer that the 3.7% of Renewable includes Small hydro.

domestic_supply_2015 = total_production_2015 / 0.985
import_2015 = 0.015 * domestic_supply_2015

coal_2015 = round(0.344 * domestic_supply_2015)

renewable_2015 = 200    # Source: Own estimate, extrapolated from 2014, + Bac Lieu 1 online
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

print("""
Vietnam electricity production by fuel type (GWh)
Source IEA 1990-2014, various estimates for 2015
Hydro includes Small Hydro and pumped storage
""")
print(production_past)
print()

#
#%% Power Development Plan 7 adjusted
#

PDP7A_annex1 = pd.read_fwf("data/PDP7A/annex1.txt",
                           usecols=["year", "id", "fuel", "capacity_MW"],
                           )

PDP7A_annex1.replace({"fuel": {"TD": "Hydro",
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

print("""
Summary of 2016-2030 new capacity listed in PDP7A annex 1, MW
Renewable includes Small Hydro
""")
print(PDP7A_annex1.groupby("fuel").capacity_MW.sum())
print("""
*: Backup coal units in case all the renewable sources do not meet the set target (27GW by 2030).
""")

