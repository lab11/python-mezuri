#!/usr/bin/env python3

import datetime
import argparse
import requests
import csv
import dateutil.parser

import mezuri
DB_IP = '146.148.49.96'

# Raw format from wunderground:
# ['TimeEDT', 'TemperatureF', 'Dew PointF', 'Humidity', 'Sea Level PressureIn',
# 'VisibilityMPH', 'Wind Direction', 'Wind SpeedMPH', 'Gust SpeedMPH',
# 'PrecipitationIn', 'Events', 'Conditions', 'WindDirDegrees', 'DateUTC<br />']
#
# Sample row:
# ['12:53 AM', '69.1', '62.1', '78', '30.01', '10.0', 'Calm', 'Calm', '-',
# 'N/A', '', 'Clear', '0', '2014-08-30 04:53:00<br />']
#
# 'TimeEDT'				'12:53 AM'
# 'TemperatureF'		'69.1'
# 'Dew PointF'			'62.1'
# 'Humidity'			'78'
# 'Sea Level PressureIn',	 '30.01'
# 'VisibilityMPH'		'10.0'
# 'Wind Direction'		'Calm'
# 'Wind SpeedMPH'		'Calm'
# 'Gust SpeedMPH',		'-'
# 'PrecipitationIn'		'N/A'
# 'Events'				''
# 'Conditions'			'Clear'
# 'WindDirDegrees'		'0'
# 'DateUTC<br />'		'2014-08-30 04:53:00<br />']

def create_table(mt, airport, year, month, day):
	print('Creating table wunderground-{}-{}-{}-{}'.format(airport, year, month, day))
	schema = {'timestamp': mezuri.ColumnTypes.datetime,
			  'tempF':     mezuri.ColumnTypes.number,
			  'humidity':  mezuri.ColumnTypes.number,
			  }
	mt.create('wunderground-{}-{}-{}-{}'.format(airport, year, month, day), schema)

def strip_html(iterable):
	for l in iterable:
		if len(l) == 0:
			continue
		l = l.decode('utf-8')
		l = l.replace('<br />', '')
		yield l

def add_data(mt, airport, year, month, day):
	print("Fetching data from wunderground...")
	URL = 'http://www.wunderground.com/history/airport/{}/{}/{}/{}/DailyHistory.html?format=1'.format(
			airport, year, month, day)
	r = requests.get(URL)
	c = csv.reader(strip_html(r.iter_lines()))
	check_names = False
	data = []
	for row in c:
		if not check_names:
			#if row[0] != 'TimeEDT':
			#	print("WARN: Skipping {}-{}-{}-{}. Expected row[0] is 'TimeEDT', but was {}".format(
			#		airport, year, month, day, row[0]))
			#	break
			if row[1] != 'TemperatureF':
				print("WARN: Skipping {}-{}-{}-{}. Expected row[1] is 'TemperatureF', but was >>{}<<".format(
					airport, year, month, day, row[1]))
				break
			if row[3] != 'Humidity':
				print("WARN: Skipping {}-{}-{}-{}. Expected row[3] is 'Humidity', but was >>{}<<".format(
					airport, year, month, day, row[3]))
				break
			if row[13] != 'DateUTC':
				print("WARN: Skipping {}-{}-{}-{}. Expected row[13] is 'DateUTC', but was >>{}<<".format(
					airport, year, month, day, row[13]))
				break
			check_names = True
			continue
		data.append({
			'timestamp': dateutil.parser.parse(row[13]+'Z'),
			'tempF': float(row[1]),
			'humidity': float(row[3])
			})

	print('Adding data...')
	mt.add_rows(data)

def get_data(mt, airport, year, month, day):
	print('Get the data back...')
	rows = mt.get_rows(100)
	for i,row in enumerate(rows):
		print('row {}'.format(i))
		for k,v in row.items():
			print('  {:<10}: {}'.format(k,v))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Weather Underground Import Script")
	parser.add_argument('--ip', type=str, default=DB_IP)
	parser.add_argument('--airport', type=str, default='KARB') # Ann Arbor
	parser.add_argument('--year', type=int, default=2013)
	parser.add_argument('--month', type=int, default=8)
	parser.add_argument('--day', type=int, default=30)

	args = parser.parse_args()

	print('Making a connection to Mezuri...')
	mt = mezuri.MezuriTable('http://'+args.ip+'/odktables', 'mezuri-10100233')

	create_table(mt, args.airport, args.year, args.month, args.day)
	add_data(mt, args.airport, args.year, args.month, args.day)
	get_data(mt, args.airport, args.year, args.month, args.day)
