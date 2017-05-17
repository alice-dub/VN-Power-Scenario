# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#


"""
Defines the baseline power plan

Up to 2015-12-31, based on historical installed capacity listed in EVN 2016 report
From 2016 onwards, based on future capacity additions listed in PDP7A
  not including coal plants listed as backup for renewables
Nuclear replaced by Coal

Renewable4 includes small hydro
"""

from init import pd, VERBOSE, show
from init import fuels, addcol_Renewable4

from data_past import capacity_past, production_past, capacity_factor_past, capacity_2015_EVN

from data_PDP7A import (PDP7A_annex1, capacities_PDP7A, capacity_total_plan, production_PDP7A,
                        capacity_factor_PDP7A)

from PowerPlan import PowerPlan

#%%


def fill_in(serie):
    """Returns the investments needed to reach the capacity objectives
    approximately because cast as integer
    """
    capacity_2015 = capacity_past.cumsum().loc[2015, serie.name]
    a = (serie[2020] - capacity_2015) / 15
    b = (serie[2025] - serie[2020]) / 15
    c = (serie[2030] - serie[2025]) / 15
    return pd.Series(name=serie.name,
                     data=[a, 2 * a, 3 * a, 4 * a, 5 * a,
                           b, 2 * b, 3 * b, 4 * b, 5 * b,
                           c, 2 * c, 3 * c, 4 * c, 5 * c],
                     index=range(2016, 2031),
                     dtype="int64")


#%%  Capacity additions

# 2016 - 2030 capacity additions for Coal, Gas, Oil, BigHydro

additions = PDP7A_annex1.replace({"fuel": {"Nuclear": "Gas"}})

additions = additions.groupby(["year", "fuel"]).capacity_MW.sum()
additions = additions.unstack()
additions.drop("ND*", axis=1, inplace=True)

# 2016 - 2030 capacity additions for the four renewable technologies

additions["Solar"] = fill_in(capacities_PDP7A.Solar)
additions["Wind"] = fill_in(capacities_PDP7A.Wind)
additions["Biomass"] = fill_in(capacities_PDP7A.Biomass)
additions["SmallHydro"] = fill_in(capacities_PDP7A.SmallHydro)
additions["Import"] = fill_in(capacities_PDP7A.Import)

# 1974 - 2015 capacity additions and cleanup

additions = pd.concat([capacity_past, additions])

additions = additions[fuels + ["PumpedStorage", "Import"]].fillna(0)

# 2031 - 2050 scenario definition

increment = {"Coal": 0, "Gas": 750, "Oil": 20, "BigHydro": 0,
             "SmallHydro": 50, "Biomass": 50, "Wind": 900, "Solar": 1000,
             "PumpedStorage": 50, "Import": 50, "Coal CCS": 0, "Gas CCS": 0, "Biomass CCS": 0}

for y in range(2031, 2051):
    additions.loc[y] = increment


#%% Old plant retirement program

plant_life = pd.Series({"Coal": 40, "Gas": 25, "Oil": 30,
                        "BigHydro": 100, "SmallHydro": 60, "Biomass": 25, "Wind": 20, "Solar": 25,
                        "Coal CCS": 40, "Gas CCS": 25, "Biomass CCS": 25,
                        "PumpedStorage": 100, "Import": 100})


retirement = pd.DataFrame()

for tech in plant_life.index:
    retirement[tech] = additions[tech].shift(plant_life[tech])

retirement.fillna(0, inplace=True)

# Fix to meet PDP7A objective more precisely
retirement.loc[2017, "BigHydro"] = 200
retirement.loc[2018, "BigHydro"] = 200
retirement.loc[2019, "BigHydro"] = 200

retirement.loc[2017, "Oil"] = 100
retirement.loc[2018, "Oil"] = 100
retirement.loc[2019, "Oil"] = 100

# Smooth the retirement program a bit, especially Gas 2025
retirement = pd.rolling_mean(retirement, 2)
retirement.loc[1974] = 0

#%%


def extend(serie, endpoint, newname, past=capacity_factor_past, future=capacity_factor_PDP7A):
    """Extends the  past   series
       going through the 2020, 2025, 2030 values defined in the  future  series
       and then to the 2050 endpoint value
    """
    r = past[serie]
    a = (r.loc[2013] + r.loc[2014] + r.loc[2015]) / 15
    b = future.loc[2020, serie] / 5
    c = future.loc[2025, serie] / 5
    d = future.loc[2030, serie] / 5
    s = pd.Series(name=newname,
                  data=[4 * a + b, 3 * a + 2 * b, 2 * a + 3 * b, a + 4 * b, 5 * b,
                        4 * b + c, 3 * b + 2 * c, 2 * b + 3 * c, b + 4 * c, 5 * c,
                        4 * c + d, 3 * c + 2 * d, 2 * c + 3 * d, c + 4 * d, 5 * d],
                  index=range(2016, 2031))
    r = r.append(s)
    d *= 5
    e = endpoint
    s = pd.Series(name=newname,
                  data=[d + (e - d) * (i + 1) / 20 for i in range(20)],
                  index=range(2031, 2051))
    return r.append(s)


#%% Electricity production

capacityfactor = pd.DataFrame()

capacityfactor["Coal"] = extend("Coal", 0.6, "Coal")
capacityfactor["Gas"] = extend("Gas", 0.6, "Gas")
capacityfactor["Oil"] = 0.25
capacityfactor["BigHydro"] = extend("BigHydro", 0.4, "BigHydro")
capacityfactor["SmallHydro"] = extend("SmallHydro", 0.6, "SmallHydro")
capacityfactor["Biomass"] = extend("Renewable", 0.3, "Biomass")
capacityfactor["Wind"] = extend("Renewable", 0.3, "Wind")
capacityfactor["Solar"] = extend("Renewable", 0.23, "Solar")

capacityfactor = capacityfactor.where(capacityfactor < 1)

net_import = extend("Import", 7000, "Import", production_past, production_PDP7A)


#%% Main statement

baseline = PowerPlan("Baseline - PDP7A extended", additions, retirement, capacityfactor, net_import)

print("""
******************************************
***            Power Plan              ***
******************************************
""")

baseline.summarize()
#baseline.detail()
#
#baseline.plot_additions()
#baseline.plot_retirement()
#baseline.plot_capacity_mix()
#baseline.plot_production_mix()
baseline.plot_plan("baseline.pdf")


#%% Validation: compares to PDP7A

show("""
*****************************************************
***     Comparing our baseline with PDP7          ***
*****************************************************
""")

compared = ["Coal", "Gas", "BigHydro", "Renewable4", "Nuclear"]

tocompare = baseline.capacities.loc[[2020, 2025, 2030]]
tocompare["Gas"] = tocompare.Gas + tocompare.Oil
tocompare["Nuclear"] = 0
addcol_Renewable4(tocompare)
tocompare = tocompare[compared]

relerror = (tocompare - capacities_PDP7A) / capacities_PDP7A
relerror = relerror[compared]

show("PDP7A")
show(capacities_PDP7A[compared])
show()
show("Baseline scenario, Gas includes Oil")
show(tocompare)
show()
show("Relative error")
show(relerror)
show("Note: Gas 2030 is larger in baseline because we replace nuclear with gas")


#%% Compares PDP7A

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


if VERBOSE:
    cf = pd.concat([capacity_factor_past, capacity_factor_PDP7A])
    cf = cf.where(cf < 1)
    cf = cf[["Coal", "Gas", "Hydro", "Renewable"]]
    ax = cf.plot(ylim=[0, 1], xlim=[1995, 2030],
                 title="Power generation capacity factors by fuel type")
    ax.axvline(2015, color="k")


#b = production_past[fuels].astype("int64")
#
#show("Past - Electricity production (GWh)")
#show(b)
#show()
#
#
#relerr = ((production_baseline - b) / b).loc[1990:2015]
#show("Relative error")
#show(relerr)

#%% Fuel use
#
#MtCoal_per_GWh = fuel_use_PDP7A.Coal / production_PDP7A.Coal
#
#show(MtCoal_per_GWh)
#
#a = MtCoal_per_GWh[2020]
#b = MtCoal_per_GWh[2025]
#da = (b - a) / 5
#c = MtCoal_per_GWh[2030]
#db = (c - b) / 5
#s = pd.Series(name="Coal",
#              data=np.concatenate([np.arange(a - 10 * da, b, da),
#                                   np.arange(b, c + 21 * db, db)]),
#              index=range(2010, 2051))
#
#show(s)
#
#coal_use_baseline = s * production_baseline.Coal.loc[2010:]
#
#show(fuel_use_PDP7A.Coal)
#show(coal_use_baseline)
#
##TODO: Check against statistics
