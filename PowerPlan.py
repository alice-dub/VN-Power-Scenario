# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
"""Represent a power development program including history, plan and our extension."""
from collections import namedtuple
import hashlib

import matplotlib.pyplot as plt

from init import fuels, sources, technologies, start_year, end_year
from init import GWh, TWh, MW, GW

#%%


class PowerPlan(namedtuple('PowerPlan',
                           ['additions', 'retirement', 'capacity_factor', 'net_import',
                            'capacities', 'production'])):
    """A power development program."""

    def __new__(cls, additions, retirement, capacity_factor, net_import):
        capacities = (additions - retirement).cumsum()
        production = capacities * capacity_factor * 8760 / 1000
        production["Import"] = net_import
        production = production[sources].fillna(0)
        production["Total"] = production.sum(axis=1)
        return super().__new__(cls, additions, retirement, capacity_factor, net_import,
                               capacities, production)

    @property
    def digest(self):
        return hashlib.md5(self.__repr__().encode('utf-8')).hexdigest()[0:4]

    def __str__(self):
        """Include a digest of the content."""
        return "Power development program #" + self.digest + ": " + self.__doc__

    def summary(self):
        """Summary of a power development program, time series shown for key years only."""
        milestones = [start_year, 2020, 2025, 2030, 2040, end_year]
        return (
            str(self) + '\n\n'
            + "Annual generation capacity addition by fuel type (MW)\n"
            + str(self.additions.loc[milestones, technologies].round()) + '\n\n'
            + "Old capacity retirement by fuel type (MW)\n"
            + str(self.retirement.loc[milestones, fuels].round()) + '\n\n'
            + "Generation capacity by fuel type (MW)\n"
            + str(self.capacities.loc[milestones, technologies].round()) + '\n\n'
            + "Electricity production (GWh)\n"
            + str(self.production.loc[milestones].round()) + '\n\n'
            + "Capacity factors\n"
            + str(self.capacity_factor.loc[milestones].round(2)) + '\n')

    def summarize(self):
        """Print object's summary."""
        print(self.summary())

    def plot_additions(self, ax, legend=True):
        self.additions[sources].plot(ax=ax, title="Added capacity (MW)",
                                     linestyle='', marker='o', legend=legend)
        ax.axvline(2015, color="k")
        ax.axvline(2030, color="k")

    def plot_retirement(self, ax, legend=True):
        self.retirement[sources].plot(ax=ax, title="Retired capacity (MW)", legend=legend)
        ax.axvline(2015, color="k")
        ax.axvline(2030, color="k")

    def plot_capacity_mix(self, ax, legend=True):
        mix = (self.capacities[sources] * MW / GW)
        mix.plot(ax=ax, title="Total generation capacity (GW)", legend=legend)
        ax.axvline(2015, color="k")
        ax.axvline(2030, color="k")

    def plot_production_mix(self, ax, legend=True):
        mix = (self.production[sources] * GWh / TWh)
        mix.plot(ax=ax, title="Electricity production (TWh)", legend=legend)
        ax.axvline(2015, color="k")
        ax.axvline(2030, color="k")

    def plot_plan(self, filename):
        """Three panels plot of a power development program: production, capacity, additions."""
        fig, axarr = plt.subplots(3, 1, figsize=[10, 15], sharex=True)
        fig.suptitle(str(self), fontsize=15)
        self.plot_additions(axarr[2], True)
        self.plot_capacity_mix(axarr[1], False)
        self.plot_production_mix(axarr[0], True)
#        axarr[0].legend(bbox_to_anchor=(1.05, 0), loc='lower left', borderaxespad=0.)
        fig.tight_layout()
        plt.subplots_adjust(top=0.94)
        fig.savefig(filename)
