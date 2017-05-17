# VN-CSS-Scenario
A recursive model of electricity production in Vietnam

(c) Dr. Minh Ha-Duong, CNRS, 2017

All files licensed under the  Creative Commons Attribution-ShareAlike 4.0 International
see file LICENSE.TXT
unless noted otherwise


Directory organization:

1. Files in data/ are raw data collected (PDF, XLS, web pages) from the web. Another copy should be in Zotero

2. Intermediate CSV or TXT if necessary, are also in data/

3. Files starting with data_X mostly make available the data found in data/X/

4. Files starting with an Upper case define the class with that name

5. Files starting with plan_ instanciate a PowerPlan object

6. Files starting with param_ instanciate a Parameter object

7. Files in  tables.tocompare are used for regression testing. Use "make reg_tests_reset" to populate/update it.

