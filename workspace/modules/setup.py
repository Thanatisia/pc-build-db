"""
Setup Project
"""

import os
import sys
import dblib

class Setup():
	def __init__(self):
		self.table_properties = [
			{
				"name" : "profiles",
				"columns" : {
					"ROW_ID" : {
						"type" : "INTEGER",
						"key" : "PRIMARY KEY",
						"null" : False,
						"default" : None,
						"unique" : True,
						"others" : ""
					},
					"username" : {
						"type" : "VARCHAR(255)",
						"key" : "NIL",
						"null" : False,
						"default" : None,
						"unique" : True,
						"others" : ""
					},
					"password" : {
						"type" : "VARCHAR(255)",
						"key" : "NIL",
						"null" : False,
						"default" : None,
						"unique" : True,
						"others" : ""
					},
					"email" : {
						"type" : "VARCHAR(255)",
						"key" : "NIL",
						"null" : False,
						"default" : None,
						"unique" : True,
						"others" : ""
					}
				}
			}
		]
	def run(self):
		def db():
			"""
			Setup Database File
			"""
			number_of_tables = len(self.table_properties)
			for table_ID in range(number_of_tables):
				"""
				Dynamically create tables based on definition
				"""
				curr_table = self.table_properties[table_ID]
				table_name = curr_table["name"]
				table_cols = curr_table["columns"]
				# print("Creating table [{}] with\n\tColumn Definitions [{}]".format(table_name, table_cols))
				result = csdb_utils.create_table(csdb_mgt.conn, table_name, table_cols, True, None, True, True)
				# print("Result: {}".format(result))
		db()

def init():
	global csdb_mgt, csdb_utils, csdb_queries, ws, test

	# External Class Objects
	csdb_mgt = dblib.SQLiteDBMgmt("PCPartsList.db")
	csdb_utils = csdb_mgt.BaseUtilities()
	csdb_queries = csdb_mgt.Queries()

def main():
	print("=== Setup ===")

if __name__ == "__main__":
	init()
	main()
