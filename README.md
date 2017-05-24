# VN-CSS-Scenario
A recursive model of electricity production in Vietnam

(c) Dr. Minh Ha-Duong, CNRS, 2017  < minh.haduong@gmail.com >

All files licensed under the  Creative Commons Attribution-ShareAlike 4.0 International
see file LICENSE.TXT unless noted otherwise


Reproductibility in three steps:
  git clone https://github.com/MinhHaDuong/VN-CSS-Scenario.git
  cd VN-CCS-Scenario/ 
  make


Installation and use:

 The code is in Python 3.5
it imports  hashlib, sys, copy, functools  from the standard library
it imports  pandas, mathplotlib, numpy  from the scientific python core packages

The builds uses a standard  Makefile  with

  make         run the model, all sensitivity analysis to build all tables and figures.

  make test    perform regression tests, docstests, and scripted tests (if any)

  make reg_tests_reset   copy results tables from the current dir into tables.tocompare/

  make clean   delete results files

  make cleaner delete results files and Python cache files


Directory organization:

1. Files in data/ are raw data collected (PDF, XLS, web pages) from the web.

2. Intermediate CSV or TXT (when used), are also in data/

3. Files starting with data_X mostly make available the data found in data/X/

4. Files starting with an Upper case define the class with that name

5. Files starting with plan_ instanciate a PowerPlan object

6. Files starting with param_ instanciate a Parameter object

7. Files in  tables.tocompare are used for regression testing. Use "make reg_tests_reset" to populate/update it.


TODO:

Expand the time horizon to two generations of coal power plants, about 80 years

Compute average age of early scrapping in CCS scenario 

Modelize the economics of retrofitting plants

Check earlier Python 3 versions

Consider SCons and Waf

Revise docstrings

Profile

Optimize

Parallelize

