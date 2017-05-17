# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#

from init import pd

"""Emission factors

Source : IPCC SRREN
 Table A.II.4 | Aggregated results of literature review of LCAs of GHG emissions
 from electricity generation technologies (g CO2eq/kWh)
 Median of the literature reviewed
"""

emission_factor = pd.Series({"Coal": 1001, "Gas": 469, "Oil": 840, "BigHydro": 4,
                             "SmallHydro": 4, "Biomass": 18, "Wind": 12, "Solar": 46,
                             "CoalCCS": float('NaN'), "GasCCS": float('NaN'),
                             "BioCCS": float('NaN')})

#Assumption: VN imports from China and Lao
emission_factor["Import"] = 0.5 * emission_factor["Coal"] + 0.5 * emission_factor["BigHydro"]
