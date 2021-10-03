"""
PC Parts Picker Profile Database Management System (DBMS)

:: Features
	- C.R.U.D
	Create/Add
		- Database
		- Table
		- Row
	Read
		- Database
		- Row
		- Column
		- Index
	Update
		- Modify Row
		- Modify Cell / Index
	Delete
		- Table
		- Row
	- Recovery
		- Export/Backup
			- Write To
				- CSV
				- Backup SQLite file
				- XML
				- JSON
				- Raw Text File
		- Import/Recover
			- Read from 
				- CSV
				- XML
				- JSON
				- Raw Text File
	
:: Database
	Type: SQLite
	Name: PCPartsList

	Table: profiles
	Columns:
		===================================================================================================
		ROW_ID, name, 				type, 		key, 			null, 		autoincrement, 	default-value
		===================================================================================================
		1, 		ROW_ID, 			INTEGER, 	PRIMARY KEY, 	NOT NULL, 	AUTOINCREMENT, 	NIL
		2, 		username,			TEXT,  						NOT NULL, 
		3, 		password (hash), 	TEXT, 	 					NOT NULL,
		4, 		email, 				TEXT,						NOT NULL,

	Table: parts
	Columns:
		======================================================================================================
		name, 							type, 		key, 			null, 		autoincrement, 	default-value
		======================================================================================================
		ROW_ID, 						INTEGER, 	PRIMARY KEY, 	NOT NULL, 	AUTOINCREMENT, 	NIL
		case_name,						TEXT,  						NULL, 						""
		case_manufacturer,				TEXT,						NULL,						""
		case_price,						FLOAT,						NULL,						0.00
		motherboard_name,				TEXT,  						NULL, 						""
		motherboard_manufacturer,		TEXT,						NULL,						""
		motherboard_price,				FLOAT,						NULL,						0.00
		cooling_device_name,			TEXT,  						NULL,						""
		cooling_device_manufacturer,	TEXT,						NULL,						""
		cooling_device_price,			FLOAT,						NULL,						0.00
		io_devices_name,				TEXT,  						NULL,						""
		io_device_manufacturer,			TEXT,						NULL,						""
		io_devices_price,				FLOAT,						NULL,						0.00

	
"""

import os
import sys
import sqlite3 as db
import csv						# To export to csv
import modules.dblib as dblib
from pathlib import Path

""" General Functions """


""" Classes """

def init():
	"""
	Initialize & Create during startup
	- Variables
	- Classes
	"""
	global cs_dbmgt, csdb_utils, csdb_queries
	cs_dbmgt = dblib.DBMgmt("test.db")
	csdb_utils = cs_dbmgt.BaseUtilities()
	csdb_queries = cs_dbmgt.Queries()

def startup():
	"""
	Processes to run during boot/startup
	"""
	init()

def main():
	print("Hello World")
	cs_dbmgt.verify_info()
	res = csdb_utils.create_table(cs_dbmgt.conn, 
		"test", {
			"ROW_ID" : {
				# INTEGER PRIMARY KEY NOT NULL AUTOINCREMENT 
				"type" : "INTEGER",
				"key" : "PRIMARY KEY",
				"null" : False,
				"default" : None
			},
			"name" : {
				# VARCHAR(255) NOT NULL
				"type" : "VARCHAR(255)",
				"key" : "NIL",
				"null" : False,
				"default" : None
			}
		}, True, None, True, True
	)
	print("Result: {}".format(res))
	table_exists = csdb_utils.query_exec(cs_dbmgt.conn, None, "SELECT name FROM sqlite_master WHERE type='table';", False,True, "all", "Data retrieved successfully.")
	print(table_exists)
	if "test" in table_exists[0]:
		print("Table {} Exists.".format("test"))

if __name__ == "__main__":
	startup()
	main()