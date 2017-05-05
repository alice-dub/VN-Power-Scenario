# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#
from data import PDP7A_annex1


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
