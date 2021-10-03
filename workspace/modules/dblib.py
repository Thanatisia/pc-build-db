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
def get_parent_dir(file_path=__file__):
	""" Get the parent directory of a file/folder
	:: Params
		file_path
			Description: The path of the file/folder you want to get the parent directory of
			Default: __file__ = Your current source file

	:: Syntax
		Path({path-to-file}).parent
	"""
	return Path(file_path).parent

""" Classes """
class SQLiteDBMgmt():
	"""
	SQLite3 Database Class
	"""
	def __init__(self, db_name, db_path=os.path.join(get_parent_dir(__file__), "res", "database")):
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

		def query_exec(self, conn, cursor=None, query_stmt="", commit=True, get_result=False, fetch="all", completion_msg="Query executed successfully."):
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
			"""
			# Variables
			result = None

			# --- Validation
			# Data Validation: Null Value
			if cursor == None:
				cursor = conn.cursor()

			# --- Processing

			# Execute Query Statement
			try:
				cursor.execute(query_stmt)
				if completion_msg != "":
					print(completion_msg)
			except Exception as e:
				print("Exception: {}".format(str(e)))

			# Commit changes in the database (i.e. like in Git/Github)
			if commit:
				# Confirm commiting
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

		def create_table(self, conn, table_name, col_definitions=None, validate_exists=False, cursor=None, commit=True, get_result=False, completion_msg="Table has been created successfully."):
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
								"key" : "PRIMARY|FOREIGN",
								"null" : False (Not Null),
								# "autoincrement" : True (AUTOINCREMENT), (REMOVED UNTIL FURTHER NOTICE)
								"default" : None
							}
						}
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


					## Compilation
					col_definition_str += "{} {} {} {} {}".format(col, curr_col_type, curr_col_key, curr_col_null, curr_col_default)
					if ROW_ID != len(columns) - 1:
						col_definition_str += ", "
					ROW_ID += 1

				# Create CREATE Query
				if validate_exists == True:
					query += " {} ".format("IF NOT EXISTS")
				query += "{} ({});".format(table_name, col_definition_str)
				print("Query: {}".format(query))

				# Execute command
				res = self.query_exec(conn, cursor, query, commit, get_result, completion_msg)
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