"""
Security Library for general useful security functions
"""

import os
import sys

# Hashing Algorithms
import hashlib

def encrypt_sha256(uInput="", encoding_algorithm="utf-8"):
	"""
	Wrapper to use hashlib.sha256(<input>) to encrypt input in sha256
	"""
	if uInput != "":
		return hashlib.sha256(uInput.encode(encoding_algorithm)).hexdigest()

def encrypt_PBKDF2_HMAC(uInput="", hash_algorithm="sha256", encoding_algorithm="utf-8", salt=os.urandom(32), iterations=100000, digest_key_size=128):
	"""
	Wrapper to generate key using PBKDF2_HMAC for Salt + Hashing
	
	:: Parameters
		uInput
			Description: Your user Input to encrypt with salt & hash (i.e. your password)
			Type: String

		hash_algorithm
			Description: Your Hashing Algorithm to use (i.e. md5, sha1, sha256)
			Type: String
			Default: sha256 => sha-256

		encoding_algorithm
			Description: Used to convert the input text based off the encoding algorithm (i.e. UTF-8|ANSI etc)
			Type: String
			Default: utf-8

		salt
			Description: The salt portion of your (salt + hash)ing encryption algorithm; 
				- The salt is a randomized string/integer that is sprinkled and mixed into the hashing digest algorithm 
				- so as to mix the result and make it difficult to check unless you have the exact formula.
			Type: String|Integer|Function
			Options:
				String: "<any salt>"
				Integer: Size/Length of the randomized salt
				Function: Any randomizer function of the user's choice
					- i.e. 
						- os.random(32)
			Default: 
				os.urandom(number_of_bytes)	
				- Where 
					number_of_bytes = length/size of the string; 
					Default: 32 = 32bytes

		iterations
			Description: Number of times/rotations SHA-256 hashing is applied
			Type: Integer
			Default: 100,000
		
		digest_key_size
			Description: The length/size of the digest key (in bytes)
				- useful if you require a longer key for something like using this key in AES
			Type: Integer
			Default: 128 (128 bytes)

	:: Remarks
		- You need to store the salt and the key using any methods
			- JSON
			- SQL
			- CSV
			- Raw text file
		- This is used to be retrieved on login and compared with the user input after encryption
	"""
	if type(salt) == type(int):
		# Length/Size of random string
		# Generate salt text
		salt = os.urandom(salt)

	key = hashlib.pbkdf2_hmac(
		hash_algorithm,						# Your Hash digest algorithm for HMAC
		uInput.encode(encoding_algorithm),	# Convert user input / password to bytes
		salt,								# provide the salt; Default: Generate Salt using os.random(32) => Returns random bytes suitable for cryptographic use
		iterations,							# Number of iterations of the hash digest algorithm, Recommended to use at least 100,000
		digest_key_size						# dklen; Get a [digest_key_size] byte key; useful if you require a longer key for something like using this key in AES
	)

	# Storage
	storage = salt + key

	return storage



def main():
	print("Beginning debugging for {}".format(__file__))

if __name__ == "__main__":
	main()