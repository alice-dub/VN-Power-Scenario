# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#


"""
Assess the scenarios

"""
import sys
import numpy as np
from functools import lru_cache

from init import pd, fuels, sources
from init import start_year, end_year, n_year, years
from init import kW, MW, USD, MUSD, GUSD, GWh, MWh, TWh, kWh, Btu, MBtu, TBtu, g, t, kt, Mt, Gt

from plan_baseline import baseline
from plan_withCCS import withCCS
from param_reference import reference


#%% Accounting functions


@lru_cache(maxsize=32)
def discountor(discount_rate):
    return pd.Series(data=np.logspace(0, n_year - 1, n_year, base=1 / (1 + discount_rate)),
                     index=years)


def present_value(series, discount_rate):
    """series can be a series or a dataframe"""
    return series.mul(discountor(discount_rate), axis=0).sum()


def discount(value, year, discount_rate):
    return value * discountor(discount_rate).loc[year]


def residual_value(additions, plant_accounting_life, fuel):
    lifetime = plant_accounting_life[fuel]
    idx = additions.index
    n = len(idx)
    remaining_fraction = pd.Series(0, index=idx)
    for i in range(min(lifetime, n)):
        # On average, plant opens middle of the year
        remaining_fraction.iloc[n - i - 1] = 1 - (i + 0.5) / lifetime
    s = pd.Series(0, index=years, name=fuel)
    s[2050] = (remaining_fraction * additions[fuel]).sum()
    return s

#%%


class Run():

    def __init__(self, plan, parameter):
        self.plan = plan
        self.parameter = parameter

        def pv(variable):
            return present_value(variable, parameter.discount_rate).sum()

        self.total_production = pv(plan.production[sources])

        self.investment = (plan.additions * MW
                           * parameter.construction_cost * USD / kW
                           / MUSD)
        self.total_investment = pv(self.investment)

        self.salvage_value = pd.concat([residual_value(plan.additions,
                                                       parameter.plant_accounting_life,
                                                       fuel)
                                        for fuel in sources],
                                       axis=1)
        self.total_salvage_value = pv(self.salvage_value)

        self.fixed_OM_cost = (plan.capacities * MW *
                              parameter.fixed_operating_cost * USD / kW
                              / MUSD)
        self.total_fixed_OM_cost = pv(self.fixed_OM_cost)

        self.variable_OM_cost = (plan.production * GWh
                                 * parameter.variable_operating_cost * USD / MWh
                                 / MUSD)
        self.total_variable_OM_cost = pv(self.variable_OM_cost)

        self.heat_used = (plan.production * GWh
                          * parameter.heat_rate * Btu / kWh
                          / TBtu)
        self.fuel_cost = (self.heat_used * TBtu
                          * parameter.heat_price * USD / MBtu
                          / MUSD)
        self.total_fuel_cost = pv(self.fuel_cost)

        self.total_cost = (self.total_investment - self.total_salvage_value
                           + self.total_fixed_OM_cost + self.total_variable_OM_cost
                           + self.total_fuel_cost)

        self.lcoe = self.total_cost / self.total_production

        self.emissions = (plan.production * GWh
                          * parameter.emission_factor * g / kWh
                          / kt)
        self.emissions["Total"] = self.emissions.sum(axis=1)
        self.total_emissions = self.emissions["Total"].sum() * kt / Gt

        self.external_cost = (self.emissions["Total"] * kt
                              * parameter.carbon_price * USD / t
                              / MUSD)
        self.total_external_cost = pv(self.external_cost)

    def __str__(self):
        return '#' + self.plan.digest() + "-" + self.parameter.digest()

    def summarize(self):
        print(self, " - Summary")
        print()
        print(self.plan)
        print(self.parameter)
        print("System LCOE: ", round(100 * self.lcoe, 2), " US cent / kWh")
        print("CO2 emissions", round(self.total_emissions, 1), "Gt CO2eq")

    def print_total(self):
        print(self, " - Totals")
        print()
        print(self.total())
        print()
        print("GHG emissions over ", start_year, "-", end_year, "by source (Mt CO2eq)")
        print()
        print(self.emission_sum())

    def total(self):
        def f(cost):
            return [round(cost * MUSD / GUSD), "bn USD"]
        d = pd.DataFrame()
        d["Power produced"] = [(self.total_production * GWh / TWh).round(), "Twh"]
        d["System LCOE"] = [round(self.lcoe * (MUSD / GWh) / (USD / MWh), 1), "USD/MWh"]
        d["Total cost"] = f(self.total_cost)
        d[" Construction"] = f(self.total_investment)
        d[" Fuel cost"] = f(self.total_fuel_cost)
        d[" O&M"] = f(self.total_fixed_OM_cost + self.total_variable_OM_cost)
        d[" Salvage value"] = f(-self.total_salvage_value)
        d["CO2 emissions"] = [round(self.total_emissions, 1), "GtCO2eq"]
        d["CO2 cost"] = f(self.total_external_cost)
        d["Cost with CO2"] = f(self.total_cost + self.total_external_cost)
        d = d.transpose()
        d.columns = [str(self), 'Unit']
        return d

    def carbon_intensity(self):
        key_years = [start_year, 2030, 2050]
        p = self.plan.production.loc[key_years, 'Total']
        p.name = "GWh"
        e = self.emissions.loc[key_years, 'Total']
        e.name = "ktCO2eq"
        intensity = (e * kt) / (p * GWh) / (g / kWh)
        intensity.name = str(self)
        return intensity.round()

    def emission_sum(self):
        s = self.emissions[sources].sum() * kt / Mt
        s = s.round()
        s.name = str(self)
        return s

#TODO: use __repr__ returns a string
    def detail(self):
        print(str(self), " - Detailed results tables")
        print()
        print("Construction costs (M$)")
        print(self.investment.loc[start_year:, fuels].round())
        print()
        print("Fixed operating costs (M$)")
        print(self.fixed_OM_cost.loc[start_year:, fuels].round())
        print()
        print("Variable operating costs (M$)")
        print(self.variable_OM_cost.loc[start_year:, sources].round())
        print()
        print("Heat used (TBtu)")
        print(self.heat_used.loc[start_year:, sources].round())
        print()
        print("Fuel costs (M$)")
        print(self.fuel_cost.loc[start_year:, sources].round())
        print()
        print("GHG emissions (ktCO2eq including CO2, CH4 and N20)")
        print(self.emissions.loc[start_year:, sources + ["Total"]].round())


class RunPair():
    """Two courses of action, compared in one environment"""

    def __init__(self, baseline, alternate, parameter):
        self.BAU = Run(baseline, parameter)
        self.ALT = Run(alternate, parameter)

    def __str__(self):
        s = str(self.BAU.parameter) + '\n\n'
        s += "BAU = " + str(self.BAU.plan) + '\n'
        s += "ALT = " + str(self.ALT.plan)
        return s

    def total(self):
        units = self.BAU.total().iloc[:, 1]
        total_BAU = self.BAU.total().iloc[:, 0]    # Only the values
        total_ALT = self.ALT.total().iloc[:, 0]
        total_diff = total_ALT - total_BAU
        d = pd.concat([total_BAU, total_ALT, total_diff, units], axis=1)
        d.columns = ['BAU', 'ALT', 'difference', 'Units']
        return d

    def emission_sum(self):
        es_BAU = self.BAU.emission_sum()
        es_ALT = self.ALT.emission_sum()
        es_diff = es_ALT - es_BAU
        d = pd.concat([es_BAU, es_ALT, es_diff], axis=1)
        d.columns = ['BAU', 'ALT', 'difference']
        return d

    def carbon_intensity(self):
        ci_BAU = self.BAU.carbon_intensity()
        ci_ALT = self.ALT.carbon_intensity()
        ci_diff = ci_ALT - ci_BAU
        d = pd.concat([ci_BAU, ci_ALT, ci_diff], axis=1)
        d.columns = ['BAU', 'ALT', 'difference']
        return d

    def carbon_value(self):
        s = self.total()['difference']
        return - s['Total cost'] / s['CO2 emissions']

    def summary(self):
        s = "*******************\n\n"
        s += str(self) + '\n\n'
        s += 'Present value cost of avoided emissions: '
        s += str(round(self.carbon_value(), 1)) + " USD/tCO2eq"
        s += '\n\n'
        s += str(self.total())
        s += '\n\n'
        s += 'Emissions by source (ktCO2eq)\n'
        s += str(self.emission_sum())
        s += '\n\n'
        s += 'Average Carbon Intensity (g/kWh)\n'
        s += str(self.carbon_intensity())
        return s


if (len(sys.argv) == 2) and (sys.argv[0] == "Run.py"):
    if sys.argv[1] == "summarize":
        print("""
******************************************
***             Results                ***
******************************************
""")
        pair = RunPair(baseline, withCCS, reference)
        print(pair.summary())
    else:
        print('Call this script with "summarize" to print the summary')
