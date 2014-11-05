#!/usr/bin/env bash

for f in {1..31}; do ./weather.py --year 2014 --month 1 --day $f; done
for f in {1..29}; do ./weather.py --year 2014 --month 2 --day $f; done
for f in {1..31}; do ./weather.py --year 2014 --month 3 --day $f; done
for f in {1..30}; do ./weather.py --year 2014 --month 4 --day $f; done
for f in {1..31}; do ./weather.py --year 2014 --month 5 --day $f; done
for f in {1..30}; do ./weather.py --year 2014 --month 6 --day $f; done
for f in {1..31}; do ./weather.py --year 2014 --month 7 --day $f; done
for f in {1..31}; do ./weather.py --year 2014 --month 8 --day $f; done
for f in {1..30}; do ./weather.py --year 2014 --month 9 --day $f; done
for f in {1..31}; do ./weather.py --year 2014 --month 10 --day $f; done
for f in {1..30}; do ./weather.py --year 2014 --month 11 --day $f; done
for f in {1..31}; do ./weather.py --year 2014 --month 12 --day $f; done
