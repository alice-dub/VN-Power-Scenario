# encoding: utf-8
#
# (c) Minh Ha-Duong, 2017
#     minh.haduong@gmail.com
#     Creative Commons Attribution-ShareAlike 4.0 International
#
#
""" Plot Generation capacity by technology, 1975 - 2050 for both scenarios

Usage:
   python3 figure-capacities.py plot filename.[pdf|png|...]

The output formats available depend on the backend being used.
"""

import sys
import matplotlib.pyplot as plt

from init import MW, GW, fuels
from plan_baseline import baseline
from plan_withCCS import withCCS


def plot_capacity_mix(plan, ax, sources_toshow):
    mix = (plan.capacities[sources_toshow] * MW / GW)
    colors = ["k", '0.75', "y", "b", "c", "g", "m", "r", "k", "0.75", "g"]
    lines = ["-", '-', "-", "-", "-", "-", "-", "-", "--", "--", "--"]
    plt.ylabel('GW')
    mix.plot(ax=ax, title=str(plan), color=colors, style=lines, linewidth=4.0)
    ax.axvline(2015, color="k")
    ax.axvline(2030, color="k")


fig, axarr = plt.subplots(2, 1, figsize=[8, 12])
fig.suptitle("Generation capacity by technology, 1975 - 2050", fontsize=15)

plot_capacity_mix(baseline, axarr[0], fuels[0:8])

plot_capacity_mix(withCCS, axarr[1], fuels)

fig.tight_layout()
plt.subplots_adjust(top=0.94)

if __name__ == '__main__':
    if (len(sys.argv) == 3) and (sys.argv[1] == "plot"):
        fig.savefig(sys.argv[2])
