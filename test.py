#!/usr/bin/env python3

import datetime

import mezuri

DB_IP = '146.148.49.96'

print('Making a connection to Mezuri...')
mt = mezuri.MezuriTable('http://'+DB_IP+'/odktables', 'mezuri-10100233')

print("Create the table...")
schema = {'timestamp': mezuri.ColumnTypes.datetime,
          'value':     mezuri.ColumnTypes.number}
mt.create('python-mezuri-test', schema)

data = [{'timestamp': datetime.datetime.now(),
         'value':     10},
        {'timestamp': datetime.datetime.now(),
         'value':     22}]

print('Adding data...')
mt.add_rows(data)

print('Get the data back...')
rows = mt.get_rows(100)
for i,row in enumerate(rows):
	print('row {}'.format(i))
	for k,v in row.items():
		print('  {:<10}: {}'.format(k,v))
