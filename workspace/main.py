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

	Table: designs
	Columns:
		Total columns: 37
		==================================================================================================================
		name, 							type, 		key, 			null, 		autoincrement, 	default-value,	remarks
		==================================================================================================================
		ROW_ID, 						INTEGER, 	PRIMARY KEY, 	NOT NULL, 	AUTOINCREMENT, 	NIL
		case_name,						TEXT,  						NULL, 						"",				multiline
		case_manufacturer,				TEXT,						NULL,						"",				multiline
		case_price,						FLOAT,						NULL,						0.00,			multiline
		motherboard_name,				TEXT,  						NULL, 						"",				multiline
		motherboard_manufacturer,		TEXT,						NULL,						"",				multiline
		motherboard_price,				FLOAT,						NULL,						0.00,
		cpu_name,						TEXT,  						NULL, 						"",				multiline
		cpu_manufacturer,				TEXT,						NULL,						"",				multiline
		cpu_price,						FLOAT,						NULL,						0.00,
		gpu_name,						TEXT,  						NULL, 						"",				multiline
		gpu_manufacturer,				TEXT,						NULL,						"",				multiline
		gpu_price,						FLOAT,						NULL,						0.00,
		psu_name,						TEXT,  						NULL, 						"",				multiline
		psu_manufacturer,				TEXT,						NULL,						"",				multiline
		psu_power_output,				TEXT,						NULL,						"0W",			multiline; {nW}
		psu_price,						FLOAT,						NULL,						0.00,
		cooling_device_name,			TEXT,  						NULL,						"",				multiline
		cooling_device_manufacturer,	TEXT,						NULL,						"",				multiline
		cooling_device_price,			FLOAT,						NULL,						0.00,
		io_devices_name,				TEXT,  						NULL,						"",				multiline
		io_device_manufacturer,			TEXT,						NULL,						"",				multiline
		io_devices_price,				FLOAT,						NULL,						0.00,
		memory_device_name,				TEXT,  						NULL, 						"",				multiline
		memory_device_manufacturer,		TEXT,						NULL,						"",				multiline
		memory_device_size,				TEXT,						NULL,						"",				multiline; x{GiB|MiB}
		memory_device_price,			FLOAT,						NULL,						0.00,
		storage_device_name,			TEXT,  						NULL, 						"",				multiline
		storage_device_manufacturer,	TEXT,						NULL,						"",				multiline
		storage_device_size,			TEXT,						NULL,						"",				multiline; x{GiB|MiB}
		storage_device_price,			FLOAT,						NULL,						0.00,
		peripheral_category,			TEXT,						NULL,						"",				multiline
		peripheral_name,				TEXT,						NULL,						"",				multiline
		peripheral_manufacturer,		TEXT,						NULL,						"",				multiline
		peripheral_price,				FLOAT,						NULL,						0.00,
		operating_system_name,			TEXT,						NULL,						"",				multiline
		operating_system_price,			FLOAT,						NULL,						0.00,			IF Linux => 0.00

:: Logic


"""

import os
import sys
import sqlite3 as db
import csv						# To export to csv
import modules.dblib as dblib
import modules.security as sec
from pathlib import Path

""" General Functions """


""" Classes """
class Tests():
	def test_1():
		csdb_mgt.verify_info()
		res = csdb_utils.create_table(csdb_mgt.conn, 
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
		table_exists = csdb_utils.query_exec(csdb_mgt.conn, None, "SELECT name FROM sqlite_master WHERE type='table';", False,True, "all", "Data retrieved successfully.")
		print(table_exists)
		if "test" in table_exists[0]:
			print("Table {} Exists.".format("test"))


class Workspace(object):
	"""
	Main Workspace for project
	"""
	def __init__(self):
		"""
		Initialize
		"""
		self.security = self.Security()
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
		self.options = {
			"Quit" : {
				"syntax" : ["q", "quit", "(q)uit"],
				"function" : None,
				"parameters" : None
			},
			"Login" : {
				"syntax" : ["l", "login", "(l)ogin"],
				"function" : self.security.login,
				"parameters" : None
			},
			"Register" : {
				"syntax" : ["r", "register", "(r)egister"],
				"function" : self.security.registration,
				"parameters" : None
			}
		}

	def setup(self):
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
	
	def main_menu(self):
		"""
		Index Page: Main Menu
		"""
		line = ""
		# while line != "q":
		# 	for k,v in self.options.items():
		# 		print("{} : {}".format(" | ".join(v["syntax"]), k))
		# 	line = input("Please enter an option: ")

		# 	for opt_Keywords, opt_Params in self.options.items():
		# 		syntaxes = opt_Params["syntax"]
		# 		functions = opt_Params["function"]
		# 		parameters = opt_Params["parameters"]
		# 		if line in syntaxes:
		# 			# Execute function
		# 			if parameters == None:
		# 				if functions != None:
		# 					functions()
		# 			else:
		# 				functions(parameters)

		# 	if self.security.token:
		# 		# Success
		# 		self.home_page()
		

	def home_page(self):
		"""
		Post-Login Home Page
		"""
		print("Welcome to PCPartsList Database Manager!")

	def main(self):
		"""
		- Create SQLite Database
		"""
		self.setup()
		
		# Main Menu
		self.main_menu()


	class Security():
		""" Security Functions """
		def __init__(self):
			"""
			Initialization
			"""
			self.uname = ""
			self.token = False	# used for validating login status
		
		def login(self):
			"""
			Login Functions

			:: Security Factor
				1. Hash the user input in the same line as the function
				2. Do not store user input and password query in variable
			"""
			print("Login")
			
			# Get User Name
			self.uname = input("Username: ")

			# 1. Get Password Hash, 
			# 2. Ask user to input password and 
			# 3. Compare
			if sec.encrypt_sha256(input("Password: ")) == csdb_utils.retrieve(csdb_mgt.conn, ws.table_properties[0]["name"], "username,password",  "username=\"{}\"".format(self.uname), fetch="one", completion_msg="")[1]:
				print("Login Successful")
				self.token = True
			else:
				print("Login failed.")

		def registration(self):
			"""
			Registration Functions

			:: Security Factor
				1. Hash the password
				2. Do not store user input in variable

			:: Steps
				1. 
			"""
			print("Sign Up")

			# Get Info & Store in Database
			self.uname = input("Username: ")
			email = input("Email (Please ensure your syntax is [email@domain.com]): ")

			ret_code = csdb_utils.insert(
				csdb_mgt.conn, ws.table_properties[0]["name"], 
				{
					"username" : "\"{}\"".format(self.uname), 
					"password" : "\"{}\"".format(sec.encrypt_sha256(input("Password: "))), 
			 		"email"    : "\"{}\"".format(email)
				}, 
				commit=True, completion_msg=""
			)
			print(ret_code)


def init():
	"""
	Initialize & Create during startup
	- Variables
	- Classes
	"""
	global csdb_mgt, csdb_utils, csdb_queries, ws, test

	# External Class Objects
	csdb_mgt = dblib.SQLiteDBMgmt("PCPartsList.db")
	csdb_utils = csdb_mgt.BaseUtilities()
	csdb_queries = csdb_mgt.Queries()

	# Internal Class Objects
	ws = Workspace()
	test = Tests()

def startup():
	"""
	Processes to run during boot/startup
	"""
	init()

def main():
	print("Hello World")
	ws.main()


if __name__ == "__main__":
	startup()
	main()