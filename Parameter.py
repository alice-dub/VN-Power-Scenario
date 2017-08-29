# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
"""Parameter  describes a technical and economic environment."""

from collections import namedtuple
import hashlib

from init import pd, sources, start_year


class Parameter(namedtuple('Parameter',
                           ['discount_rate',
                            'plant_accounting_life',
                            'construction_cost',
                            'fixed_operating_cost',
                            'variable_operating_cost',
                            'heat_rate',
                            'heat_price',
                            'emission_factor',
                            'capture_factor',
                            'carbon_price'])):
    """Parameter  describes a technical and economic environment.

    Bundle a power generation technology database, carbon price trajectory and discount rate.
    digest      content digest, a short checksum
    summary()   contents summary, time series represented by initial level and trend.
    __new__()   constructor, default not extended
    __repr__()  detailed representation as  string, default not extended

    """

    @property
    def digest(self):
        return hashlib.md5(self.__repr__().encode('utf-8')).hexdigest()[0:6]

    def __str__(self):
        return "Parameters #" + self.digest + ": " + self.__doc__

    def summary(self):
        """Summarize object contents, time series are defined by initial level and trend."""
        summary = pd.DataFrame()
        s = self.plant_accounting_life[sources]
        s.name = "Plant accounting life (year)"
        summary = summary.append(s)
        s = self.emission_factor[sources]
        s.name = "Emission factor (gCO2eq/kWh)"
        summary = summary.append(s)
        s = self.capture_factor.loc[start_year, sources]
        s.name = "Capture factor (gCO2/kWh)"
        summary = summary.append(s)
        s = self.construction_cost.loc[start_year]
        s.name = "Overnight construction costs ($/kW)"
        summary = summary.append(s)
        s = self.construction_cost.diff().loc[start_year + 1]
        s.name = "Overnight construction costs trend ($/kW/y)"
        summary = summary.append(s)
        s = self.fixed_operating_cost.loc[start_year]
        s.name = "Fixed operating costs ($/kW)"
        summary = summary.append(s)
        s = self.fixed_operating_cost.diff().loc[start_year + 1]
        s.name = "Fixed operating costs trend ($/kW/yr)"
        summary = summary.append(s)
        s = self.variable_operating_cost.loc[start_year]
        s.name = "Variable operating costs ($/kWh)"
        summary = summary.append(s)
        s = self.heat_rate.loc[start_year]
        s.name = "Heat rate (Btu/kWh)"
        summary = summary.append(s)
        s = self.heat_price.loc[start_year]
        s.name = "Heat price ($/MBtu)"
        summary = summary.append(s)

        return (
            str(self) + '\n\n'
            + str(summary[sources].round(1)) + '\n\n'
            + "Carbon price ($/tCO2eq)\n"
            + str(self.carbon_price.loc[[start_year, 2030, 2040, 2050]]) + '\n\n'
            + "Discount rate: " + str(self.discount_rate))

    def summarize(self):
        """Print object's summary."""
        print(self.summary())
