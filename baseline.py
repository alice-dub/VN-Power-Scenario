# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#


"""
Defines the baseline scenario

Up to 2015-12-31, based on historical installed capacity listed in EVN 2016 report
From 2016 onwards, based on future capacity additions listed in PDP7A
  not including coal plants listed as backup for renewables
Nuclear replaced by Coal

Renewable4 includes small hydro
"""

import pandas as pd
from data import fuel_types, PDP7A_annex1, capacities_PDP7A, capacity_past

#%%

baseline = PDP7A_annex1.replace({"fuel": {"Nuclear": "Gas"}})

baseline = baseline.groupby(["year", "fuel"]).capacity_MW.sum()
baseline = baseline.unstack()
baseline.drop("ND*", axis=1, inplace=True)

print(baseline)


def fill_in(serie):
    """Returns the investments needed to reach the capacity objectives"""
    capacity_2015 = capacity_past.cumsum().loc[2015, serie.name]
    a = (serie[2020] - capacity_2015) / 15
    b = (serie[2025] - serie[2020]) / 15
    c = (serie[2030] - serie[2025]) / 15
    s = pd.Series(name=serie.name,
                  data=[a, 2 * a, 3 * a, 4 * a, 5 * a,
                        b, 2 * b, 3 * b, 4 * b, 5 * b,
                        c, 2 * c, 3 * c, 4 * c, 5 * c],
                  index=range(2016, 2031),
                  dtype="int64")
#    print(s)
#    print(s.cumsum())
    return s

baseline["Solar"] = fill_in(capacities_PDP7A.Solar)
baseline["Wind"] = fill_in(capacities_PDP7A.Wind)
baseline["Biomass"] = fill_in(capacities_PDP7A.Biomass)
baseline["SmallHydro"] = fill_in(capacities_PDP7A.SmallHydro)
baseline = pd.concat([capacity_past, baseline])
baseline.drop(["Renewable4", "LargeHydro", "InterHydro", "Hydro", "Import", "Renewable"],
              axis=1, inplace=True)
baseline = baseline.fillna(0)

print(baseline[fuel_types + ["PumpedStorage"]])

increment = {"Coal": 0, "Gas": 750, "Oil": 0, "BigHydro": 0,
             "SmallHydro": 50, "Biomass": 50, "Wind": 900, "Solar": 1000,
             "PumpedStorage": 50}

for y in range(2031, 2051):
    baseline.loc[y] = increment

print("Vietnam annual generation capacity addition by fuel type (MW)")
print(baseline)
print()

print("Vietnam generation capacity by fuel type (MW)")
print(baseline.cumsum())
print()

mix = (baseline[fuel_types] / 1000).drop("Oil", axis=1).cumsum()
ax = mix.plot(title="Baseline scenario\nVietnam generation capacity by fuel type (GW)")
ax.axvline(2015, color="k")
ax.axvline(2030, color="k")

#%% Check the capacity numbers vs. PDP7A objectives
print("Baseline scenario")
print(baseline.cumsum().loc[[2020, 2025, 2030]])
print()

print("PDP7A")
print(capacities_PDP7A[["Coal", "Gas", "BigHydro", "Renewable4", "Nuclear"]])
print()

relerror = (baseline.cumsum().loc[[2020, 2025, 2030]] - capacities_PDP7A) / capacities_PDP7A
relerror = relerror[["Coal", "Gas", "Oil", "BigHydro", "Renewable4", "Nuclear"]]

print("Relative error")
print(relerror)
print("Coal 2030 is larger in baseline because we replace nuclear with coal")
#FIXME: The relative error on Hydro is big
