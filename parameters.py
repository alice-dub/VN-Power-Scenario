# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#

"""Model's parameters of the model"""

discount_rate = 0.05

# This is both:
#   economic life, to assess residual value by linear depreciation
#   physical life, to retire from production capacities
plant_life = {"Coal": 40, "Gas": 25, "Oil": 30, "BigHydro": 100,
              "SmallHydro": 60, "Biomass": 25, "Wind": 20, "Solar": 25,
              "PumpedStorage": 100}
