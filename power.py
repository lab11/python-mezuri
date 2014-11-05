#!/usr/bin/env python3

import datetime
import argparse
import requests
import csv
import json
import dateutil.parser
import pytz

import mezuri
DB_IP = '146.148.49.96'

LOCATIONS = {
		'2193A0' : 'Home1',
		'107FF2' : 'Home2',
		'26059D' : 'Lab11',
		}

# Raw format of interesting packet (have a 'location_str' key) from the dump:
# {
#   "_id" : { "$oid" : "52fd4e0dc8b91666eae36f7d" },
#   "gateway_id" : "2193A0",
#   "location_str" : "USA|Michigan|Ann Arbor|1885 Fuller|Laundry Room",
#   "watts" : 1114,
#   "profile_id" : "nMR0xcWInF",
#   "description" : "TED - whole house power monitor",
#   "address" : "281471825231739",
#   "public" : true,
#   "voltage" : 116.1,
#   "time" : { "$numberLong" : "1392332301684" },
#   "port" : 17530
# }

# {
#   "_id" : { "$oid" : "52fd4e4ac8b91666eae375b5" },
#   "gateway_id" : "26059D",
#   "location_str" : "University of Michigan|BBB|4908",
#   "watts" : 1889,
#   "profile_id" : "nMR0xcWInF",
#   "description" : "TED - whole lab energy meter",
#   "kva" : 2.119,
#   "voltage_blue" : 119.9,
#   "time" : { "$numberLong" : "1392332362737" },
#   "current_blue" : 11.3,
#   "public" : true,
#   "pf" : 0.891,
#   "voltage" : 119.9,
#   "address" : "281473061227379",
#   "voltage_black" : 119.9,
#   "current_red" : 3.4,
#   "port" : 80,
#   "current_black" : 2.5,
#   "voltage_red" : 119.9 
# }

def create_table(mt, data):
	try:
		location = LOCATIONS[data['gateway_id']]
	except KeyError:
		print("\nWARN: No location known for gateway_id {}".format(data['gateway_id']))
		return None
	table_name = 'TED-{}'.format(location)
	print('Creating table {}'.format(table_name))
	schema = {
			'timestamp': mezuri.ColumnTypes.datetime,
			'watts': mezuri.ColumnTypes.number,
			'voltage': mezuri.ColumnTypes.number,
			}
	mt.create(table_name, schema)
	return mt

def format_data(data):
	localtz = pytz.timezone('America/New_York')
	t = datetime.datetime.fromtimestamp(int(data['time']['$numberLong'])/1000)
	t = localtz.localize(t)
	new = {
		'_id' : data['_id']['$oid'],
		'timestamp': t,
		'watts' : data['watts'],
		'voltage': data['voltage'],
		}
	return new

def get_data(mt, airport, year, month, day):
	print('Get the data back...')
	rows = mt.get_rows(100)
	for i,row in enumerate(rows):
		print('row {}'.format(i))
		for k,v in row.items():
			print('  {:<10}: {}'.format(k,v))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Power Data Upload Script")
	parser.add_argument('--ip', type=str, default=DB_IP)

	args = parser.parse_args()

	tables = {}
	rows = {}
	for gateway in LOCATIONS:
		rows[gateway] = []

	for line in open('power/ted.json'):
		data = json.loads(line)
		if 'location_str' not in data:
			continue
		if data['gateway_id'] not in tables:
			print('Making a connection to Mezuri...')
			mt = mezuri.MezuriTable('http://'+args.ip+'/odktables', 'mezuri-10100233')
			mt = create_table(mt, data)
			if mt:
				tables[data['gateway_id']] = mt
			else:
				continue
		new_row = format_data(data)
		rows[data['gateway_id']].append(new_row)
		if len(rows[data['gateway_id']]) >= 100000:
			print("Uploading {} rows for {}: {}".format(
				len(rows[data['gateway_id']]),
				data['gateway_id'],
				LOCATIONS[data['gateway_id']]
				))
			tables[data['gateway_id']].add_rows(rows[data['gateway_id']])
			rows[data['gateway_id']] = []

	print("Finished json file, uploading remaining entries")
	for gateway in LOCATIONS:
		print("Uploading {} rows for {}: {}".format(
			len(rows[gateway]),
			gateway,
			LOCATIONS[gateway]
			))
		tables[gateway].add_rows(rows[gateway])
		rows[gateway] = []
