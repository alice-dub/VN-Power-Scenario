# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#

from init import pd

"""Emission factors

Source : IPCC SRREN Methodology Annex II, Methodology
Lead Authors: William Moomaw (USA), Peter Burgherr (Switzerland), Garvin Heath (USA),
Manfred Lenzen (Australia, Germany), John Nyboer (Canada), Aviel Verbruggen (Belgium)
Table A.II.4 page 982 "Aggregated results of literature review of LCAs of GHG emissions
from electricity generation technologies (g CO2eq/kWh)"

Median of the literature reviewed for Coal to Solar.
(Min + Max)/2 for CCS technologies
"""

emission_factor = pd.Series({"Coal": 1001, "Gas": 469, "Oil": 840, "BigHydro": 4,
                             "SmallHydro": 4, "Biomass": 18, "Wind": 12, "Solar": 46,
                             "CoalCCS": (98 + 396) / 2, "GasCCS": (65 + 245) / 2,
                             "BioCCS": (- 1368 + (-594)) / 2})

#Assumption: VN imports from China and Lao
emission_factor["Import"] = 0.5 * emission_factor["Coal"] + 0.5 * emission_factor["BigHydro"]
