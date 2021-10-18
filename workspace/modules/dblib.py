"""
Database Utilities for
	- SQLite3
"""
import os
import sys
import sqlite3 as db
import csv					# To export to csv
from pathlib import Path

""" General Functions """
def get_parent_dir(file_path=__file__, jumps=1):
	""" Get the parent directory of a file/folder
	:: Params
		file_path
			Description: The path of the file/folder you want to get the parent directory of
			Type: String
			Default: __file__ = Your current source file

		jumps
			Description: Number of parent directories you want to go backwards
			Type: Integer
			Default: 1

	:: Syntax
		Path({path-to-file}).parent
	"""
	curr_dir = file_path
	for i in range(jumps):
		curr_dir = Path(curr_dir).parent
	return curr_dir

""" Classes """
class SQLiteDBMgmt(object):
	"""
	SQLite3 Database Class
	"""
	def __init__(self, db_name, db_path=os.path.join(get_parent_dir(__file__, 2), "res", "database")):
		global utils
		utils = self.BaseUtilities()
		self.db_name = db_name
		self.db_path = db_path
		self.full_path = os.path.join(db_path, db_name)
		self.conn = utils.open_db(self.full_path)	# Create Database object
		print("Opened Database")

	def __exit__(self):
		self.db_name = ""
		self.db_path = ""
		self.full_path = os.path.join(self.db_path, self.db_name)
		self.conn = utils.close_db(self.conn)
		print("Closed Database")
	
	class Queries():
		"""
		SQL Statement Queries
		"""
		# Static
		def __init__(self):
			global stmt_list_tables
			stmt_list_tables =  "SELECT name FROM sqlite_master WHERE type='table';"

		def gen_stmt(self, table, table_columns=None, keyword="select"):
			"""
			Generate SQLite Query Statements

			:: Params
				table
					Description: The name of the table you want to manipulate
					Type: String

				table_columns
					Description: The columns in the table
					Type: String
					Remarks: Please seperate each table name columns with delimiter ','

				keyword
					Description: The Query keyword you want to use (i.e. SELECT, INSERT)
					Type: String
					Options:
						- select : SELECT
						- create : CREATE
						- insert : INSERT
						- update : UPDATE
						- delete : DROP
			
			:: Returns
				Value: queries[keyword]
				Type: String
			"""
			stmt = ""
			queries = {
				"select" : "SELECT",
				"create" : "CREATE TABLE IF NOT EXISTS {}".format(table),
				"insert" : "INSERT INTO {} VALUES ({})".format(table, table_columns),
				"update" : "UPDATE",
				"delete" : "DROP {}",
				"list-table" : self.stmt_list_tables,
			}
			return queries[keyword]

	class BaseUtilities():
		"""
		SQLite3 Database - Utilities Class
		"""
		def open_db(self, db_name, other_params=None):
			"""
			Create / Open Database

			:: Params
				db_name
					Description: Your Database Name
					Type: String

				db_mode
					Description: The Mode you want your database to open
					Type: String
					Options:
						r	| Read
						w	| Write (Overwrite)
						rw	| Read + Write
						wr	| Write + Read
						b	| Binary
						rb	| Read + Binary
						a	| Append
						a+ 	| Append + Read
					Default: a+ | Append + Read

				other_params
					Description: Other connect() parameters you want to use
					Type: Dictionary|List
					Syntax:
						db.connect(..,.., *other_params) => List
						db.connect(..,.., **other_params) => Dictionary
			"""
			conn = None
			if not (db_name == ""):
				if type(other_params) == type(dict):
					conn = db.connect(db_name, **other_params)
				elif type(other_params) == type(list):
					conn = db.connect(db_name, *other_params)
				else:
					conn = db.connect(db_name)
			return conn

		def gen_cursor(self, conn=None):
			"""
			Create cursor object using the cursor() method
			- Allows user to "point" to a memory containing the database address

			:: Params
				conn
					Description: The Database Connection
					Type: sqlite3.connect('<dbname>')
			"""
			cursor = conn.cursor()
			return cursor

		def query_exec(self, conn, cursor=None, query_stmt="", commit=True, get_result=False, fetch="all", completion_msg="Query executed successfully.", verbose=False):
			"""
			Execute a SQLite Query

			:: Params
				conn
					Description: The connection to the database
					Type: sqlite3.connect()

				cursor
					Description: Your Database cursor object
					Type: connection.cursor()

				query_stmt
					Description: Your Query Statement to execute
					Type: String

				commit
					Description: Confirm if you want to commit your query changes
					Type: Boolean

				get_result
					Description: Confirm if you would like to retrieve the results from your query
						- Related to 'fetch_quantity'
					Type: Boolean

				fetch
					Description: The fetch you want to use (fetchall|fetchmany|fetchone)
					Type: String|Dictionary
					Syntax:
						Dictionary:
							{
								"option" : "many",
								"size" : "<number-of-rows>"
							}
					Options:
						String:
							all  : fetchall()
							one  : fetchone()
						Dictionary:
							many : fetchmany(size)

				completion_msg
					Description: What to display when query is complete
					Type: String

				verbose
					Description: To set if you want messages to be displayed
					Type: Boolean
			"""
			# Variables
			result = None

			# --- Validation
			# Data Validation: Null Value
			if cursor == None:
				cursor = conn.cursor()

			# --- Processing
			if verbose:
				print(query_stmt)

			# Execute Query Statement
			try:
				cursor.execute(query_stmt)
				if completion_msg != "":
					print(completion_msg)
			except Exception as e:
				if verbose:
					err = str(e).split(": ")
					err_msg = err[0]
					err_obj = err[1].split('.')[1]
					if err_msg == "UNIQUE constraint failed":
						print("{} exists.".format(err_obj))

			# Commit changes in the database (i.e. like in Git/Github)
			if commit:
				# Confirm commiting
				if verbose:
					print("Commit completed.")
				conn.commit()

			# If want to get the result
			if get_result:
				if type(fetch) == type(dict):
					if fetch[0] == "many":
						size = fetch[1]
						result = cursor.fetchmany(size)
				else:
					if fetch == "one":
						result = cursor.fetchone()
					else:
						result = cursor.fetchall()

			return result

		def create_table(self, conn, table_name, col_definitions=None, validate_exists=False, cursor=None, commit=True, get_result=False, completion_msg="Table has been created successfully.", verbose=False):
			"""
			Create a table in database

			:: Params
				table_name
					Description: The name of the table you want to create
					Type: String

				col_definitions
					Description: These are the columns to write into the table
					Type: Dictionary
					Syntax:
						{
							"column name" : {
								"type" : "INTEGER|REAL|TEXT|BOOL",
								"key" : "PRIMARY|FOREIGN|NIL",
								"null" : False (Not Null),
								# "autoincrement" : True (AUTOINCREMENT), (REMOVED UNTIL FURTHER NOTICE)
								"default" : None,
								"unique: False (Not Unique value),
								"others": "[any other options here]"
							}
						}
						
				verbose
					Description: To set if you want messages to be displayed
					Type: Boolean
			"""
			query = "CREATE TABLE "
			table_columns = []
			col_definition_str = ""
			ROW_ID = 0
			if not (col_definitions == None):
				columns = list(col_definitions.keys())
				number_of_columns = len(columns)
				print(columns)
				for col in columns:
					curr_col_definition = col_definitions[col]
					curr_col_type = curr_col_definition["type"]
					curr_col_key = curr_col_definition["key"]
					curr_col_null = curr_col_definition["null"]
					# curr_col_autoincrement = curr_col_definition["autoincrement"]
					curr_col_default = curr_col_definition["default"]
					curr_col_unique = curr_col_definition["unique"]
					curr_col_others = curr_col_definition["others"]

					# Processing
					## Validation ##
					if curr_col_type == "" and curr_col_type == None:
						curr_col_type = input("Please enter a data type for [Column Type]: ")

					if curr_col_key == "NIL":
						curr_col_key = ""

					if curr_col_null == False:
						curr_col_null = "NOT NULL"
					else:
						curr_col_null = "NULL"

					# if curr_col_autoincrement == True:
					# 	curr_col_autoincrement = "AUTOINCREMENT"
					# else:
					# 	curr_col_autoincrement = ""
					
					if curr_col_default == None:
						curr_col_default = ""

					if curr_col_unique == True:
						curr_col_unique = "UNIQUE"


					## Compilation
					col_definition_str += "{} {} {} {} {} {} {}".format(col, curr_col_type, curr_col_key, curr_col_null, curr_col_default, curr_col_unique, curr_col_others)
					if ROW_ID != len(columns) - 1:
						col_definition_str += ", "
					ROW_ID += 1

				# Create CREATE Query
				if validate_exists == True:
					query += " {} ".format("IF NOT EXISTS")
				query += "{} ({});".format(table_name, col_definition_str)

				if verbose:
					print("Query: {}".format(query))

				# Execute command
				res = self.query_exec(conn, cursor, query, commit, get_result, completion_msg=completion_msg, verbose=verbose)
				return res

		def retrieve(self, conn, table_name, col="*", where_condition="", other_options="", cursor=None, commit=False, get_result=True, fetch="all", completion_msg="Retrieval completed.", verbose=True):
			"""
			Query from Database Table and return the result using 'SELECT'

			:: Params

				conn
					Description: Your Database Connection Object
					Type: sqlite3.connect("<database-name>")

				table_name
					Description: Your Table of choice
					Type: String

				col
					Description: The column you want to select
					Type: String
					Default: "*" = Wildcard = All
					Remarks:
						- Please seperate all columns with delimiter ','

				where_condition
					Description: a filter / specifier for what you need (i.e. WHERE table=='name')
					Type: String
					Default: ""

				other_options
					Description: Other options to use in the query
					Type: String
					Default: ""

				cursor
					Description: The cursor object generated from the connection
					Type: sqlite3.connect().cursor()
					Default: None

				commit
					Description: Confirm if you want to commit your query changes
					Type: Boolean
					Default: False

				get_result
					Description: Confirm if you want to get the result of the query
						- Correlated to the argument field 'fetch'
					Type: Boolean
					Default: True

				fetch
					Description: Confirm the number of results
					Type: String
					Default: "all"
					Options: 
						- {
								"option" : "many",
								"size" : "<number-of-rows>"
						}
						- one
						- all 

				completion_msg
					Description: The message to display on completion.
					Type: String
					Default: "Retrieval completed."

				verbose
					Description: To set if you want messages to be displayed
					Type: Boolean
			"""
			res = ""

			# Generate Query
			if where_condition != "":
				query_stmt = "SELECT {} FROM {} WHERE {}".format(col, table_name, where_condition)
			else:
				query_stmt = "SELECT {} FROM {}".format(col, table_name)

			# Data Validation: Null Value
			if other_options != "":
				query_stmt += " {} ".format(other_options)

			if verbose:
				print("Query Statement", query_stmt)

			# Execute Query
			res = self.query_exec(conn, cursor, query_stmt, commit, get_result, fetch, completion_msg, verbose)

			if verbose:
				print("Result: {}".format(res))

			# Data Validation: Null Value
			if len(res) == 0:
				res = None

			return res

		def insert(self, conn, table_name, value_definitions=None, where_condition="", other_options="", cursor=None, commit=False, get_result=True, fetch="all", completion_msg="insert completed.", verbose=False):
			"""
			Query from Database Table and return the result using 'INSERT'

			:: Params

				conn
					Description: Your Database Connection Object
					Type: sqlite3.connect("<database-name>")

				table_name
					Description: Your Table of choice
					Type: String

				values_definitions
					Description: The new values you want to add into the table mapped to the column
					Type: Dictionary
					Default: None
					Syntax:
						{
							"<column>" : <new-value>
						}
					Remarks:
						- Please take note of your data type of the variables
							- i.e.
								- String: "string-value"
								- Float (aka REAL): 1.0f
								- Int: 0
								- Boolean: True|False
					Examples:
						{
							"name" : "asura",
							"age" : 1000,
							"money" : 10000.00f
							"registered" : True
						}

				where_condition
					Description: a filter / specifier for what you need (i.e. WHERE table=='name')
					Type: String
					Default: ""

				other_options
					Description: Other options to use in the query
					Type: String
					Default: ""

				cursor
					Description: The cursor object generated from the connection
					Type: sqlite3.connect().cursor()
					Default: None

				commit
					Description: Confirm if you want to commit your query changes
					Type: Boolean
					Default: False

				get_result
					Description: Confirm if you want to get the result of the query
						- Correlated to the argument field 'fetch'
					Type: Boolean
					Default: True

				fetch
					Description: Confirm the number of results
					Type: String
					Default: "all"
					Options: 
						- {
								"option" : "many",
								"size" : "<number-of-rows>"
						}
						- one
						- all 

				completion_msg
					Description: The message to display on completion.
					Type: String
					Default: "insert completed."
			"""
			res = ""

			# Generate and Execute Query
			res = self.query_exec(conn, cursor, "INSERT INTO {} ({}) VALUES ({});".format(table_name, ",".join(list(value_definitions.keys())), ",".join(list(value_definitions.values()))), commit, get_result, fetch, completion_msg, verbose=verbose)

			# Data Validation: Null Value
			if len(res) == 0:
				res = None

			return res


		def close_db(self, conn=None):
			"""
			Close Database
			"""
			if not (conn == None):
				conn.close()
				conn = None
			return conn

	def verify_info(self, param="all"):
		"""
		Verify database details
			all : Verify all
			name : Get Name of currently opened database
			path : Get Path of currently opened database
			conn : Get Connection of currently opened database
		"""
		print(f"Verifying {param}...")
		if param == "name": 
			print("Name : {}".format(self.db_name))
		elif param == "path":
			print("Path : {}".format(self.db_path))
		elif param == "conn":
			print("Connection :	{}".format(self.conn))
		else:
			print("	Name 	    : {}".format(self.db_name))
			print("	Path 	    : {}".format(self.db_path))
			print("	Connection  : {}".format(self.conn))

def init():
	"""
	Initialize & Create during startup
	- Variables
	- Classes
	"""


def startup():
	"""
	Processes to run during boot/startup
	"""
	init()

def main():
	"""
	Debugging
	"""
	print("Hello World")

if __name__ == "__main__":
	startup()
	main()