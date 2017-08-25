# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#


"""Define a power plan with CCS.

Coal-fired power plants do dominate the generation sector of Vietnam from 2020 onward.
The total capacity of coal-fired power plants would increase to 55 GW by 2030.
CCS finally takes off in the international context, as China, Australia, South Africa
and a few other countries consider it a Nationally Appropriate Mitigation Action.
This reduces the technical barriers, and drives down the costs of CCS technology to a point where
an affluent Vietnam can afford it by 2040.
Vietnam and other countries in the region benefits CCS capacity building programs
from IEA, ASEAN, APEC and industry associations.

In this scenario, storage activities are still initially driven by the oil industry,
who seeks to extend the end life of offshore oilfield by CO2 flooding.
But the government plays a central role early on. Incentive systems (e.g. taxes, subsidy ...)
are implemented, as soon as 2020 for R&D, to setup a pilot project, with the goal to have
a commercial scale demonstrator by 2035. In parallel, the government announces that
coal fired power plants build after 2020 will have to be capture-ready.
The electricity generation sector is an active player for CO2 transport activities.

Usage:

python3 plan_withCCS.py summarize
python3 plan_withCCS.py plot filename.[pdf|png|...]
"""

import sys

from init import pd, end_year, technologies
from PowerPlan import PowerPlan

from plan_baseline import baseline

#%%

additions, retirement = baseline.additions.copy(), baseline.retirement.copy()

#%%

pilot1_year = 2024
pilot1_size = 250  # MW of gas-fired generation
assert(additions.at[pilot1_year, "Gas"] > pilot1_size)
additions.at[pilot1_year, "Gas"] -= pilot1_size
additions.at[pilot1_year, "GasCCS"] += pilot1_size

pilot2_year = 2029
pilot2_size = 750  # MW of gas-fired generation
assert(additions.at[pilot2_year, "Gas"] > pilot2_size)
additions.at[pilot2_year, "Gas"] -= pilot2_size
additions.at[pilot2_year, "GasCCS"] += pilot2_size

#%%

retrofit_start_year = 2035
assert retrofit_start_year > pilot2_year

retrofit_period = range(retrofit_start_year, end_year + 1)

# Convert all other coal capacity to Coal CCS on 2035 - 2050
retrofit_rate_coal = baseline.capacities.at[end_year, "Coal"] / len(retrofit_period)
retirement.loc[retrofit_period, "Coal"] += retrofit_rate_coal
additions.loc[retrofit_period, "CoalCCS"] = retrofit_rate_coal

# Convert all other Gas capacity to Gas CCS on 2035 - 2050
retrofit_rate_gas = ((baseline.capacities.at[end_year, "Gas"] - pilot1_size - pilot2_size
                     - additions.loc[retrofit_period, "Gas"].sum()
                      ) / len(retrofit_period))
retirement.loc[retrofit_period, "Gas"] += retrofit_rate_gas
additions.loc[retrofit_period, "GasCCS"] = retrofit_rate_gas

# Install new Gas CCS plants instead of simple Gas
additions.loc[retrofit_period, "GasCCS"] += additions.loc[retrofit_period, "Gas"]
additions.loc[retrofit_period, "Gas"] = 0

# Ramp up some BioCCS, quadratically
bioCCS_trend = 10    # The increase of annual capacity installed (MW / yr)
bioCCS_2050 = bioCCS_trend * len(retrofit_period)
bioCCS_ramp = pd.Series(range(0, bioCCS_2050, bioCCS_trend),
                        retrofit_period)
additions.loc[retrofit_period, "BioCCS"] = bioCCS_ramp

# Save a bit on Gas CCS, keeping the end_year generation unchanged
savedGasCCS = (bioCCS_ramp
               * baseline.capacity_factor.at[end_year, "BioCCS"]
               / baseline.capacity_factor.at[end_year, "GasCCS"])
additions.loc[retrofit_period, "GasCCS"] -= savedGasCCS


withCCS = PowerPlan("With CCS",
                    additions,
                    retirement[technologies],
                    baseline.capacity_factor,
                    baseline.net_import)

if __name__ == '__main__':
    if (len(sys.argv) == 2) and (sys.argv[1] == "summarize"):
        withCCS.summarize()
    if (len(sys.argv) == 3) and (sys.argv[1] == "plot"):
        withCCS.plot_plan(sys.argv[2])

#print(withCCS)
#
#withCCS.summarize()
#print(repr(withCCS))

#withCCS.plot_plan("withCCS.pdf")
