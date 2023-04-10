from src.api.apiConfig import api
import hashlib
import random
import string
from src.api.fitcrack.endpoints.rainbowTables.table import RainbowTable
#import src.api.fitcrack.endpoints.rainbowTables.data as data
import pathlib

import logging
from flask import request, redirect, send_file
from flask_restx import Resource, abort
from sqlalchemy import exc

from src.api.fitcrack.responseModels import simpleResponse, file_content
from src.api.fitcrack.argumentsParser import path
from src.database import db

from src.api.fitcrack.endpoints.rainbowTables.argumentsParser import rainbowTables_estimateparser
from src.api.fitcrack.endpoints.rainbowTables.responseModels import estimate_model

from src.api.fitcrack.responseModels import simpleResponse, file_content

log = logging.getLogger(__name__)
ns = api.namespace('rainbowTables', description='Endpoints for work with HcStats files.')

def writeTofile(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)
    print("Stored rainbow table data into: ", filename)
    
# Estimate time to generate a table
def estimate_gen_time(chain_len, chain_num, algorithm, charset, max_len):
    algorithm = algorithm.lower()
    default_chars = 26
    charset = len(charset)
    diff = charset - default_chars
    multiply_char = 1
    multiply_alg = 1
    multiply_len = 1
    if diff == 26:
        multiply_char = 1.03
    elif diff == 74:
        multiply_char = 1.05
    elif diff == 36:
        multiply_char = 1.1
    elif diff == 84:
        multiply_char = 1.25
        
    if algorithm == "sha1":
        multiply_alg = 1.03
    elif algorithm == "sha2-256":
        multiply_alg = 1.03
    elif algorithm == "sha512":
        multiply_alg = 1.15
        
    if max_len <= 5:
        multiply_len = 0.85
    elif max_len <= 10:
        multiply_len = 1
    elif max_len <= 15:
        multiply_len = 1.05
    elif max_len <= 20:
        multiply_len = 1.15
    elif max_len <= 25:
        multiply_len = 1.33
    elif max_len <= 30:
        multiply_len = 1.45
    hashes_per_sec = 300000
    return((chain_len * chain_num * multiply_char * multiply_alg * multiply_len) / hashes_per_sec)

@ns.route('/estimate')
class Estimate(Resource):
    @api.marshal_with(estimate_model)
    @api.expect(rainbowTables_estimateparser)
    def post(self):
        args = rainbowTables_estimateparser.parse_args(request)
        time = estimate_gen_time(args['chain_len'], args['chain_num'], args['algorithm'], args['charset'], args['max_len'])

        return {"time": time}, 200

# Check if given arguments are valid
def check_args_gen(args):
    if args.length_max < 1:
        print("Length must be greater than 0")
        exit(1)
    if args.length_min < 1:
        print("Length must be greater than 0")
        exit(1)
    if args.length_max > 30:
        print("Plaintext length is capped at 30")
        exit(1)
    if args.length_min > 30:
        print("Plaintext length is capped at 30")
    if args.columns < 1:
        print("Number of columns must be greater than 0")
        exit(1)
    if args.rows < 1:
        print("Number of rows must be greater than 0")
        exit(1)
    if args.length_min > args.length_max:
        print("Minimum length must be less or equal to maximum length")
        exit(1)
        
def check_args_search(args):
    if args.length_max < 1:
        print("Length must be greater than 0")
        exit(1)
    if args.length_min < 1:
        print("Length must be greater than 0")
        exit(1)
    if args.length_max > 30:
        print("Plaintext length is capped at 30")
        exit(1)
    if args.length_min > 30:
        print("Plaintext length is capped at 30")
    if args.length_min > args.length_max:
        print("Minimum length must be less or equal to maximum length")
        exit(1)

# Word generator functions
def gen_lower(n):
    def result():
        password = ""
        for _ in range(n):
            password += random.choice(string.ascii_lowercase)
        return password
    return result

def gen_upper(n):
    def result():
        password = ""
        for _ in range(n):
            password += random.choice(string.ascii_uppercase)
        return password
    return result

def gen_letters(n):
    def result():
        password = ""
        for _ in range(n):
            password += random.choice(string.ascii_letters)
        return password
    return result

def gen_special_chars(n):
    def result():
        password = ""
        for _ in range(n):
            password += random.choice(string.printable)
        return password
    return result

def gen_alphanumeric(n):
    def result():
        password = ""
        for _ in range(n):
            password += random.choice(string.ascii_letters + string.digits)
        return password
    return result

def gen_all(n):
    def result():
        password = ""
        for _ in range(n):
            password += random.choice(string.digits + string.printable)
        return password
    return result


# Reduction functions
def reduce_lower(lower, upper):
    def result(hash, col):
        plaintextKey = (int(hash, 16) ^ col) % (26 ** lower) # Conver hash to number
        plaintext = ""
        diff = upper - lower
        rang = plaintextKey % (diff + 1) + lower # Get Random length
        for _ in range(rang):
            plaintext += string.ascii_lowercase[plaintextKey % 26]
            plaintextKey //= 26
        return plaintext
    return result

def reduce_upper(lower, upper):
    def result(hash, col):
        plaintextKey = (int(hash, 16) ^ col) % (26 ** lower)
        plaintext = ""
        diff = upper - lower
        rang = plaintextKey % (diff + 1) + lower
        for _ in range(rang):
            plaintext += string.ascii_uppercase[plaintextKey % 26]
            plaintextKey //= 26
        return plaintext
    return result

def reduce_letters(lower, upper):
    def result(hash, col):
        plaintextKey = (int(hash, 16) ^ col) % (52 ** lower)
        plaintext = ""
        diff = upper - lower
        rang = plaintextKey % (diff + 1) + lower
        for _ in range(rang):
            plaintext += string.ascii_letters[plaintextKey % 52]
            plaintextKey //= 52
        return plaintext
    return result

def reduce_special_chars(lower, upper):
    def result(hash, col):
        plaintextKey = (int(hash, 16) ^ col) % (100 ** lower)
        plaintext = ""
        diff = upper - lower
        rang = plaintextKey % (diff + 1) + lower
        for _ in range(rang):
            plaintext += string.printable[plaintextKey % 100]
            plaintextKey //= 100
        return plaintext
    return result

def reduce_alphanumeric(lower, upper):
    def result(hash, col):
        plaintextKey = (int(hash, 16) ^ col) % (62 ** lower)
        plaintext = ""
        diff = upper - lower
        rang = plaintextKey % (diff + 1) + lower
        for _ in range(rang):
            plaintext += (string.ascii_letters + string.digits)[plaintextKey % 62]
            plaintextKey //= 62
        return plaintext
    return result

def reduce_all(lower, upper):
    def result(hash, col):
        plaintextKey = (int(hash, 16) ^ col) % (110 ** lower)
        plaintext = ""
        diff = upper - lower
        rang = plaintextKey % (diff + 1) + lower
        for _ in range(rang):
            plaintext += (string.printable + string.digits)[plaintextKey % 110]
            plaintextKey //= 110
        return plaintext
    return result

# Select hashing algorithm
def get_hashing_alg(input: str):
    if input == 'md5':
        return hashlib.md5
    elif input == 'sha1':
        return hashlib.sha1
    elif input == 'sha256':
        return hashlib.sha256
    elif input == 'sha512':
        return hashlib.sha512
    else:
        print("This hashing algorithm is not supported")
        exit(1)

# Select reduction function
def get_reduction_func(input: str, lower: int, upper: int):
    if input == 'lowercase':
        return reduce_lower(lower, upper), gen_lower(lower), string.ascii_lowercase
    elif input == 'uppercase':
        return reduce_upper(lower, upper), gen_upper(lower), string.ascii_uppercase
    elif input == 'letters':
        return reduce_letters(lower, upper), gen_letters(lower), string.ascii_letters
    elif input == 'special':
        return reduce_special_chars(lower, upper), gen_special_chars(lower), string.printable
    elif input == 'alphanum':
        return reduce_alphanumeric(lower, upper), gen_alphanumeric(lower), string.ascii_letters + string.digits
    elif input == 'all':
        return reduce_all(lower, upper), gen_all(lower), string.printable + string.digits
    else:
        print("This reduction function is not supported")
        exit(1)
    
    
# def crack(hash, table, path):
#     plaintext = data.search_password(hash) # Search for password in database
#     if plaintext:
#         print("Password found in database: {0}".format(plaintext[0]))
#         exit(0)
#     try: 
#         int(hash, 16)
#     except:
#         print("Hash is not in hexadecimal format")
#         exit(1)
#     table = RainbowTable(hashlib.md5, 10, reduce_lower(5, 10), gen_lower(5), "md5", "lowercase", 5, 6) # Create empty table
#     if not path.endswith("/"): # Add / to path if not present
#         path += "/"
#     table.load_from_cvs(filename= path + table) # Load table from file
#     hashing_alg = get_hashing_alg(table.table['alg'])
#     reduction_func, _, _ = get_reduction_func(table.table['rest'], int(table.table['len']), int(table.table['len_max']))
#     table.hash_func = hashing_alg
#     table.chain_len = int(table.table['chain_len'])
#     table.reduction_func = reduction_func
#     result = table.crack(hash)
    
#     id = data.get_table_id(table) # Get id of table for later update of values
    
#     if result is not None:
#         #clear()
#         print("Succes, the password is {0}".format(result))
#         data.update_table(True, id)
#         data.add_password_to_database(hash, result)
#     else:
#         #clear()
#         print("Password not found")
#         data.update_table(False, id) 
    
# def gen(length_min, length_max, restrictions, algorithm, columns, rows, filename):
#     if length_min < 5:
#         print("Minimum length of less than 5 results in many collisions, which can cause the table to be unusable")
#         print("do you wish to continue? (y/n)")
#         inp = input()
#         if inp != "y":
#             exit(1)
#     hashing_alg = get_hashing_alg(algorithm)
#     reduction_func, gen_func, charset = get_reduction_func(restrictions, length_min, length_max)
    
#     table = RainbowTable(hashing_alg, columns, reduction_func, gen_func, algorithm, restrictions, length_min, length_max)
#     if filename[-4:] != ".csv": # Add .csv to filename if not present
#         filename += ".csv"
#     estimate = estimate_gen_time(rows, columns, algorithm, len(charset), length_max)
#     print("Estimated time to generate table assuming average CPU : {0} mins, {1} seconds".format(int(estimate/60), int(estimate % 60)))
#     print("Do you wish to continue? (y/n)")
#     inp = input()
#     if inp == "n":
#         print("Exiting...")
#         exit(0)
#     elif inp == "y":
#         pass
#     else: 
#         print("Invalid input, exiting...")
#         exit(0)
#     table.gen_table(rows=rows, file=filename)
    
#     data.add_table_to_database(table, filename)
    
#     print("""rainbow table {3} parameters:
#           hash algorithm:   {0}
#           charset name:     {1}
#           charset length:   {2}
#           charset data:     {4}
#         """.format(algorithm, restrictions, len(charset), filename, charset))
    
# def search(algorithm, restrictions, length_min, length_max):
#     res = data.get_tables(algorithm, restrictions, length_min, length_max)
#     print("Found {0} tables".format(len(res)))
#     for table in res:
#         print("""
#               name :                    {0}
#               number of tries:          {1}
#               successful tries:         {2}
#               password length range:    {3} to {4} characters
#               ID:                       {5}""".format(table[0], table[1], table[2], table[4], table[5], table[3]))
#         print("Select a table using load path ID")
    
# elif args.mode == "load":
#     name = data.fetch_table(args.ID)
#     if not name: # Check if table exists
#         print("No table with this ID")
#         exit(1)
#     if not pathlib.Path(args.path).exists(): # Check if path exists
#         print("Path does not exist")
#         exit(0)
#     path = args.path + "/" + name[0][1] # Create path to file
#     if pathlib.Path(path).is_file():
#         print("File already exists, are you sure you want to rewrite it? (y/n)")
#         inp = input()
#         if inp == "y":
#             writeTofile(name[0][0], path)
#         elif inp == "n":
#             print("Exiting...")
#             exit(0)
#         else: 
#             print("Invalid input, exiting...")
#             exit(0)
#     else:
#         print("Downloading file...")
#         writeTofile(name[0][0], path)
#         print("Done")
