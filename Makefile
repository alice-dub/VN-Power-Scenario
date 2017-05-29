# Economic of co-firing in two power plants in Vietnam
#
# (c) Minh Ha-Duong, An Ha Truong 2016, 2017
# minh.haduong@gmail.com
# Creative Commons Attribution-ShareAlike 4.0 International
#

PYTHON = python3


tablepyfiles = plan_baseline.py plan_withCCS.py param_reference.py Run.py analysis.py
tables = $(patsubst %.py,%.txt,$(tablepyfiles)) table-parameters.fwf table-comparison.fwf
diffs  = $(patsubst %.py,%.diff,$(tablepyfiles))

figures = plan_baseline.pdf plan_withCCS.pdf figure-capacities.pdf figure-capacities.png

doc_tests = data_past.doctest

all-parallel:
	make all -j

all: $(tables) $(figures)

%.py: %-generator.py
	$(PYTHON) $< > $@

table-parameters.fwf: param_reference.txt
	head -13 $< | tail -11 > $@

table-comparison.fwf: Run.txt
	head -26 $< | tail -16 > $@


%.txt: %.py
	@-sed -i "s/VERBOSE = True/VERBOSE = False/" init.py
	$(PYTHON) $< summarize > $@

%.pdf: %.py
	$(PYTHON) $< plot $@

%.png: %.py
	$(PYTHON) $< plot $@

%.diff: %.txt tables.tocompare/%.txt
	@diff $^  > $@
	@if [ -s $@ ]; then exit 1; fi;

%.doctest: %.py
	$(PYTHON) -m doctest -v $< > $@

.PHONY: test reg_tests reg_tests_reset clean cleaner

test: $(doc_tests) $(script_tests) reg_tests

reg_tests: $(diffs)
	@cat $^

reg_tests_reset: $(tables)
	cp $^ tables.tocompare

clean:
	rm -f $(tables)
	rm -f $(figures)
	rm -f $(doc_tests)
	rm -f $(script_tests)
	rm -f $(diffs)

cleaner: clean
	find . -type f -name '*.pyc' -delete
	rm -rf __pycache__
	rm -f *.bak
