import datetime
import json
import random
import time
import uuid

import py4j.protocol
import py4j.java_gateway

java_gateway = py4j.java_gateway.JavaGateway()
wink = java_gateway.jvm.org.opendatakit.wink.client.WinkClient()
py4j.java_gateway.java_import(java_gateway.jvm,'java.util.*')


###
### Exceptions
###
class ConnectionError (Exception):
	pass

class TableError (Exception):
	pass

###
### Column Types
###
class ColumnTypes ():
	datetime = 'dateTime'
	string = 'string'
	number = 'number'

###
### Main Objects
###

class MezuriTable ():

	def __init__ (self, mezuri_url, mezuri_application, table_name=None):
		self.url = mezuri_url
		self.app = mezuri_application

		random.seed()

		self.table_name = table_name
		if table_name == None:
			# User must call create() before using this table
			self.table_ETag = None

		else:
			# Look up the table
			table_ETag = wink.getSchemaETagForTable(self.url,
			                                        self.app,
			                                        table_name)
			if table_ETag:
				self.table_ETag = table_ETag
				self._get_schema()

			else:
				raise(TableError('No table named "{}" found.'.format(table_name)))


	def create (self, table_name, schema):
		"""Create a Mezuri table if it does not already exist.

		Schema should be specified as a dict of {column_name: column_type}.

		Returns the ETag of the table."""

		if self.table_name == table_name:
			return

		try:
			self.table_name = table_name
			table_ETag = wink.getSchemaETagForTable(self.url, self.app, table_name)

			if table_ETag:
				self.table_ETag = table_ETag
				self._get_schema()
				return


			# If we get here the table could not be found.
			# We must create a new table.

			# Convert the schema to the correct JSON blob
			table_schema = {'orderedColumns': [],
			                'tableId': table_name,
			                'schemaETag': None}

			for column_name,column_type in schema.items():
				table_schema['orderedColumns'].append({
					'elementKey': column_name,
					'elementType': column_type,
					'elementName': column_name,
					'listChildElementKeys': '[]'})

			table_schema_json = json.dumps(table_schema)

			new_table = wink.createTableWithJSON(self.url,
			                                     self.app,
			                                     table_name,
			                                     None,
			                                     table_schema_json)
			table_ETag = wink.getSchemaETagForTable(self.url, self.app, table_name)
			self.table_ETag = table_ETag
			self.schema = schema


		except py4j.protocol.Py4JJavaError as e:
			if str(e.java_exception) == 'org.apache.wink.client.ClientWebException':
				raise(ConnectionError('Could not connect to Mezuri.'))

			raise(e)

		except Exception as e:
		 	raise(e)

	def add_rows (self, rows):
		"""Add rows to a table.

		rows should look like: [{'column_name': column value}]

		The column name _id is reserved. If specified, that will be used
		as the row id.

		"""

		table = wink.getTable(self.url, self.app, self.table_name)

		new_rows = {'rows': []}

		for i,row in enumerate(rows):
			cols = []
			row_id = None

			for column_name,column_value in row.items():

				if column_name == '_id':
					row_id = column_value
					continue

				# Convert certain types automatically
				if type(column_value) == datetime.datetime:
					column_value = column_value.strftime('%c')

				cols.append({'column': column_name,
				             'value': column_value})
			if not row_id:
				row_id = random.randint(0, 2**63)

			new_rows['rows'].append({'id': row_id,
			                         'orderedColumns': cols})

		table_json = json.dumps(new_rows)

		wink.createRowsUsingJSONBulkUpload(self.url,
		                                   self.app,
		                                   self.table_name,
		                                   self.table_ETag,
		                                   table_json,
		                                   100)

	def get_rows (self, num_rows):

		rows = wink.getRows(self.url,
		                    self.app,
		                    self.table_name,
		                    self.table_ETag,
		                    '',
		                    str(num_rows))

		output = []

		for row in rows['rows']:
			gotrow = {}
			for col in row['orderedColumns']:
				if self.schema[col['column']] == ColumnTypes.datetime:
					gotrow[col['column']] = datetime.datetime.strptime(col['value'], '%a %b %d %H:%M:%S %Y')
				elif self.schema[col['column']] == ColumnTypes.number:
					gotrow[col['column']] = float(col['value'])
				else:
					gotrow[col['column']] = col['value']
			output.append(gotrow)

		return output


	def get_table_ETag (self):
		return uuid.UUID(self.table_ETag)

	def _get_schema (self):
		# Get the schema
		schema = wink.getTableDefinition(self.url,
		                                 self.app,
		                                 self.table_name,
		                                 self.table_ETag)
		self.schema = {}
		for col in schema['orderedColumns']:
			if col['elementType'] == 'dateTime':
				self.schema[col['elementName']] = ColumnTypes.datetime
			elif col['elementType'] == 'string':
				self.schema[col['elementName']] = ColumnTypes.string
			elif col['elementType'] == 'number':
				self.schema[col['elementName']] = ColumnTypes.number

	def _uuid_to_string (self, ETag):
		return 'uuid:{}'.format(ETag)







