# encoding: utf-8
#
# (c) Minh Ha-Duong  2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#
#
import pandas as pd

PDP7A_annex1_file = "data/PDP7A/annex1.txt"
t = pd.read_fwf(PDP7A_annex1_file)
print(t)

"""Input parameters of the model"""

discount_rate = {0, 0.05, 0.08, 0.12}
