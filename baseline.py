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
from data import PDP7A_annex1, capacities_PDP7A, capacity_past_5cols


#%%

baseline = PDP7A_annex1.replace({"fuel": {"Nuclear": "Gas"}})

baseline = baseline.groupby(["year", "fuel"]).capacity_MW.sum()
baseline = baseline.unstack()
baseline = pd.concat([capacity_past_5cols, baseline])
baseline = baseline.fillna(0)

baseline.drop("ND*", axis=1, inplace=True)

baseline = baseline[["Coal", "Gas", "Oil", "BigHydro", "Renewable4"]]

increment = {"Coal": 0, "Gas": 750, "Oil": 0, "BigHydro": 0, "Renewable4": 2000}

for y in range(2031, 2051):
    baseline.loc[y] = increment

print("Vietnam annual generation capacity addition by fuel type (MW)")
print(baseline)
print()

print("Vietnam generation capacity by fuel type (MW)")
print(baseline.cumsum())
print()

mix = (baseline / 1000).drop("Oil", axis=1).cumsum()
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
