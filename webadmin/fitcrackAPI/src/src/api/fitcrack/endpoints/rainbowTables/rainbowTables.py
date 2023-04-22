from src.api.apiConfig import api
import hashlib
import random
import string
from src.api.fitcrack.endpoints.rainbowTables.table import RainbowTable
import src.api.fitcrack.endpoints.rainbowTables.data as data
from src.api.fitcrack.functions import fileUpload, shellExec
import os
import logging
from flask import request, redirect, send_file, jsonify
from flask_restx import Resource, abort
from sqlalchemy import exc
from src.api.fitcrack.responseModels import simpleResponse, file_content
from settings import RT_DIR
from src.api.fitcrack.endpoints.rainbowTables.argumentsParser import rainbowTables_estimateparser, rainbowTables_generateparser, rainbowTables_loadparser
from src.api.fitcrack.endpoints.rainbowTables.responseModels import estimate_model, RTSet_model
from src.database.models import FcHash
from src.database import db

log = logging.getLogger(__name__)
ns = api.namespace('rainbowTables', description='Endpoints for work with HcStats files.')

ALLOWED_EXTENSIONS = set(['csv'])
CSV_FIELDNAMES = ['start_point', 'endpoint_hash']

def get_hash_alg_from_code(code):
    mapping = {
    0: 'md5',
    100: 'sha1',
    900: 'md4',
    1000: 'ntlm',
    1300: 'sha2-224',
    1400: 'sha2-256',
    1700: 'sha2-512',
    3000: 'lm',
    10800: 'sha2-384',
    }
    if code not in mapping:
        raise ValueError('Unknown hash algorithm code')
    return mapping[code]

def get_code_from_hash_alg(alg):
    mapping = {
        'md5': 0,
        'sha1': 100,
        'md4': 900,
        'ntlm': 1000,
        'sha2-224': 1300,
        'sha2-256': 1400,
        'sha2-512': 1700,
        'lm': 3000,
        'sha2-384': 10800,
    }
    if alg not in mapping:
        raise ValueError('Unknown hash algorithm')
    return mapping[alg]

def writeTofile(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)
    print("Stored rainbow table data into: ", filename)
    
def getcoverage(lower, upper, charset, columns, filename):
    coverage = 0
    lines = 0
    with open(os.path.join(RT_DIR,filename)) as file:
        for count, lines in enumerate(file):
            pass
    lines = count - 5
    table_size = lines * columns
    for i in range(lower, upper + 1):
        coverage += (charset ** i)
    coverage = (table_size/coverage)*100
    coverage = round(coverage, 1)
    if coverage > 100:
        coverage = 99.9
    if coverage == 0.0:
        coverage = 0.1
    return str(coverage) + "%"
    
# Estimate time to generate a table
def estimate_gen_time(chain_len, chain_num, algorithm, charset, max_len):
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
        hash_alg = get_hash_alg_from_code(args['algorithm'])
        time = estimate_gen_time(args['chain_len'], args['chain_num'], hash_alg, args['charset'], args['max_len'])

        return {"time": time}, 200

# Check if given arguments are valid

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
        plaintextKey = (int(hash[:9], 16) ^ col) % (26 ** lower) # Conver hash to number
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
        plaintextKey = (int(hash[:9], 16) ^ col) % (26 ** lower)
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
        plaintextKey = (int(hash[:9], 16) ^ col) % (52 ** lower)
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
        plaintextKey = (int(hash[:9], 16) ^ col) % (100 ** lower)
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
        plaintextKey = (int(hash[:9], 16) ^ col) % (62 ** lower)
        plaintext = ""
        diff = upper - lower
        rang = plaintextKey % (diff + 1) + lower
        for _ in range(rang):
            plaintext += (string.ascii_letters + string.digits)[plaintextKey % 62]
            plaintextKey //= 62
        return plaintext
    return result

# Select hashing algorithm
def get_hashing_alg(input: str):
    if input == 'md5':
        return hashlib.md5
    elif input == 'sha1':
        return hashlib.sha1
    elif input == 'sha2-256':
        return hashlib.sha256
    elif input == 'sha2-512':
        return hashlib.sha512
    elif input == 'sha2-224':
        return hashlib.sha224
    elif input == 'sha2-384':
        return hashlib.sha384
    else:
        print("This hashing algorithm is not supported")
        exit(1)

# Select reduction function
def get_reduction_func(input: str, lower: int, upper: int):
    input = input.lower()
    
    if input == 'lowercase':
        return reduce_lower(lower, upper), gen_lower(lower), string.ascii_lowercase
    elif input == 'uppercase':
        return reduce_upper(lower, upper), gen_upper(lower), string.ascii_uppercase
    elif input == 'letters':
        return reduce_letters(lower, upper), gen_letters(lower), string.ascii_letters
    elif input == 'all':
        return reduce_special_chars(lower, upper), gen_special_chars(lower), string.printable
    elif input == 'alphanumeric':
        return reduce_alphanumeric(lower, upper), gen_alphanumeric(lower), string.ascii_letters + string.digits
    else:
        print("This reduction function is not supported")
        exit(1)
    
    
# def crack(hash, table, path):
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

@ns.route('/crack')
class Crack(Resource):
    def post(self):
        req = request.get_json()
        table_ids = req['tables']
        hashes = req['hashes'].split('\n')
        result = {}
        for hash in hashes.copy():
            plaintext = data.search_password(hash)
            if plaintext:
                result[hash] = plaintext[0]
                hashes.remove(hash)
        for table_id in table_ids:
            tab = data.fetch_table_from_id(table_id)
            # ID chain_len algorithm charset min_plaintext max_plaintext name tries successful_tries content
            table = RainbowTable(hashlib.md5, 10, reduce_lower(5, 10), gen_lower(5), "md5", "lowercase", 5, 6) # Create empty table
            table.load_from_csv(filename = os.path.join(RT_DIR, tab[6]))
            hashing_alg = get_hashing_alg(tab[2])
            reduction_func, _, _ = get_reduction_func(tab[3], int(tab[4]), int(tab[5]))
            table.hash_func = hashing_alg
            table.chain_len = int(tab[1])
            table.reduction_func = reduction_func
            for hash in hashes.copy():
                last_id = FcHash.query.order_by(FcHash.id.desc()).first().id
                result[hash] = table.crack(hash)
                if result[hash] is not None:
                    data.update_table(True, table_id)
                    hashes.remove(hash)
                    data.add_password_to_database(hash, result[hash])
                    hash_obj = FcHash(id = last_id + 1, job_id = 0, hash_type = int(get_code_from_hash_alg(tab[2])), hash = bytes(hash, 'utf-8'), result = bytes(result[hash].encode().hex(), 'utf-8'))
                    db.session.add(hash_obj)
                    db.session.commit()
                else:
                    result[hash] = "Password not found"
                    data.update_table(False, table_id)
        return {'items': result, 'message': 'Password lookup has finished', 'status': True}, 200
    
def gen(length_min, length_max, restrictions, algorithm, columns, rows, filename):
    hashing_alg = get_hashing_alg(algorithm)
    restrictions = restrictions.strip()
    reduction_func, gen_func, charset = get_reduction_func(restrictions, length_min, length_max)
    
    table = RainbowTable(hashing_alg, columns, reduction_func, gen_func, algorithm, restrictions, length_min, length_max)
    if filename[-4:] != ".csv": # Add .csv to filename if not present
        filename += ".csv"
    if data.check_name(filename):
       return {'message': 'Table name already exists', 'status': False}, 400
    table.gen_table(rows=rows, file=filename)
    
    data.add_table_to_database(table, filename)
    return {'message': 'Table generated', 'status': True}, 200
    
@ns.route('/generate')
class Generate(Resource):
    @api.marshal_with(simpleResponse)
    @api.expect(rainbowTables_generateparser)
    def post(self):
        args = rainbowTables_generateparser.parse_args(request)
        hash_alg = get_hash_alg_from_code(args['algorithm'])
        final = gen(args['length_min'], args['length_max'], args['restrictions'], hash_alg, args['columns'], args['rows'], args['filename'])
        return final
          
def to_dict(my_tuple):
    _, _, charset = get_reduction_func(my_tuple[8], 1, 1)
    coverage = getcoverage(my_tuple[1], my_tuple[2], len(charset), my_tuple[7], my_tuple[0])
    my_dict = {
        'name': my_tuple[0],
        'range': str(my_tuple[1]) + ' - ' + str(my_tuple[2]) + ' characters',
        'algorithm': my_tuple[3].upper(),
        'number': 0 if my_tuple[4] == 0 else (round(my_tuple[5] / my_tuple[4] * 100, 2)),
        'id': my_tuple[6],
        'chain_len': my_tuple[7],
        'coverage': coverage
    }
    return my_dict

def all_to_dict(my_tuple):
    _, _, charset = get_reduction_func(my_tuple[3], 1, 1)
    my_dict = {
        'id': my_tuple[0],
        'chain_len': my_tuple[1],
        'algorithm': my_tuple[2],
        'restrictions': charset,
        'range': str(my_tuple[4]) + ' - ' + str(my_tuple[5]) + ' characters',
        'name': my_tuple[6],
        'tries': my_tuple[7],
        'successful': my_tuple[8],
    }
    return my_dict

@ns.route('/download/<filename>')
class Download(Resource):
    def get(self, filename):
        if not data.check_name(filename):
            return {'message': 'Table does not exist', 'status': False}, 400
        return send_file(RT_DIR + '/' + filename, as_attachment=True)
    
@ns.route('/loadall')
class LoadAll(Resource):
    def get(self):
        tables = data.load_all_tables()
        new_tables = []
        for table in tables:
            table = to_dict(table)
            new_tables.append(table)
        return {'items': new_tables}, 200
    
    @api.expect(rainbowTables_loadparser)
    def post(self):
        args = rainbowTables_loadparser.parse_args(request)
        hash_alg = get_hash_alg_from_code(args['code'])
        tables = data.load_hash_type_tables(hash_alg)
        new_tables = []
        for table in tables:
            table = to_dict(table)
            new_tables.append(table)
        return {'items': new_tables}, 200
    
    
@ns.route('/<id>')
class Table(Resource):

    @api.marshal_with(RTSet_model)
    def get(self, id):
        """
        Returns information about rainbow table with data.
        """

        RainbowSet = data.select_table(id)
        RainbowSet = all_to_dict(RainbowSet)
        

        with open(os.path.join(RT_DIR, RainbowSet['name'])) as file:
            content = file.read()

        return {
            'id': RainbowSet['id'],
            'chain_len': RainbowSet['chain_len'],
            'algorithm': RainbowSet['algorithm'].upper(),
            'restrictions': RainbowSet['restrictions'],
            'range': RainbowSet['range'],
            'name': RainbowSet['name'],
            'tries': RainbowSet['tries'],
            'successful': RainbowSet['successful'],
            'data': content
        }
        
@ns.route('/add')
class rainbowAdd(Resource):

    @api.marshal_with(simpleResponse)
    def post(self):
        """
        Uploads Rainbow table files on server.
        """
        # check if the post request has the file part
        if 'file' not in request.files:
            abort(500, 'No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            abort(500, 'No selected file')

        uploadedFile = fileUpload(file, RT_DIR, ALLOWED_EXTENSIONS, suffix='.csv', withTimestamp=True)
        if uploadedFile:
            with open(os.path.join(RT_DIR, uploadedFile['filename'])) as file:
                content = file.read()
                if 'start_point' not in content:
                    abort(500, 'Wrong file format')
                if 'endpoint_hash' not in content:
                    abort(500, 'Wrong file format')
                if 'chain_len' not in content:
                    abort(500, 'Wrong file format')
                if 'alg' not in content:
                    abort(500, 'Wrong file format')
                if 'rest' not in content:
                    abort(500, 'Wrong file format')
                if 'len' not in content:
                    abort(500, 'Wrong file format')
                if 'len_max' not in content:
                    abort(500, 'Wrong file format')
                    
                my_dict = {}
                
                for line in content.split('\n'):
                    if line.strip() != '':
                        value, key = line.split(',')
                        my_dict[key] = value
                
                table = RainbowTable('', my_dict['chain_len'], '', '', my_dict['alg'], my_dict['rest'], my_dict['len'], my_dict['len_max'])
                
                data.add_table_to_database(table, uploadedFile['filename'])  
                return {'message': 'File ' + uploadedFile['filename'] + ' succesfully uploaded', 'status': True}
        else:
            abort(500, 'Wrong file format')
    