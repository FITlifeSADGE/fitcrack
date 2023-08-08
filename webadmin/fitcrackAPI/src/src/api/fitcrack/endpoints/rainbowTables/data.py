import sqlite3
from src.api.fitcrack.endpoints.rainbowTables import table
from settings import RT_DIR
import os
import pathlib

# Checks for the existence of the directory where the tables are stored and creates it if it doesn't exist
# RT_DIR == /usr/share/collections/RTables
if not pathlib.Path(RT_DIR).exists():
        pathlib.Path(RT_DIR).mkdir(parents=True, exist_ok=True)

# Checks for the existence of the database where the tables are stored and creates it if it doesn't exist     
if not pathlib.Path(os.path.join(RT_DIR, 'tables.db')).exists():
    with open(os.path.join(RT_DIR, 'tables.db'), encoding='latin-1', mode='w+') as file:
        file.write('')
        file.close()

# Changes the permissions of the database so that the apache user can access it
os.system("chmod 664 " + os.path.join(RT_DIR, 'tables.db'))
os.system("chown apache:apache " + os.path.join(RT_DIR, 'tables.db'))

# Connects to the database
con = sqlite3.connect(os.path.join(RT_DIR, 'tables.db'), check_same_thread=False)
cur = con.cursor()


def convertToBinaryData(filename):
    """Used to convert the data from the file to binary data

    Args:
        filename (str): Name of the file
    Returns:
        blobData (bytes): Binary data of the file
    """
    # Convert digital data to binary format
    with open(os.path.join(RT_DIR, filename), 'rb') as file:
        blobData = file.read()
    return blobData

# Creates the tables in the database if they don't exist
cur.execute("""CREATE TABLE IF NOT EXISTS RainbowTable(
    id INTEGER PRIMARY KEY, 
    chain_len INTEGER, 
    hashing_alg TEXT, 
    reduction_function TEXT, 
    password_length_min INTEGER, 
    password_length_max INTEGER,
    name TEXT, 
    number_of_tries INTEGER, 
    successful_tries INTEGER,
    dict_text BLOB NOT NULL)""")

cur.execute("""CREATE TABLE IF NOT EXISTS Password(
    hash TEXT PRIMARY KEY,
    plaintext TEXT
    )""")

con.commit()


def add_table_to_database(RT: table.RainbowTable, RTname):
    """Used to add a generated/uploaded table to the database

    Args:
        RT (table.RainbowTable): Rainbow table object
        RTname (str): Name of the table
    """
    chain_len = RT.chain_len
    hash_alg = RT.alg
    rest = RT.rest
    min_length = RT.len
    max_length = RT.len_max
    table_text = convertToBinaryData(RTname)
    try:
        new_ID = cur.execute("SELECT MAX(id) FROM RainbowTable").fetchone()[0] + 1
    except:
        new_ID = 1
    cur.execute("INSERT INTO RainbowTable VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0, ?)", (new_ID, chain_len, hash_alg, rest, min_length, max_length, RTname, table_text))
    con.commit()
    
def get_tables(alg: str, rest: str, length_min: int, length_max: int):
    """Used to retrieve specific information about the tables in the database
    
    Args:
        alg (str): Hashing algorithm
        rest (str): Reduction function name
        length_min (int): Minimum length of the password
        length_max (int): Maximum length of the password
    Returns:
        A list of tuples containing the information about the tables
    """
    cur.execute("SELECT name, number_of_tries, successful_tries, id, password_length_min, password_length_max FROM RainbowTable WHERE hashing_alg = ? AND reduction_function = ? AND password_length_min <= ? AND password_length_max >= ?", (alg, rest, length_min, length_max))
    return cur.fetchall()

def update_table(success: bool, id: int):
    """Used to update the number of tries and successful tries of a table

    Args:
        success (bool): Whether the password was found or not
        id (int): ID of the table
    """
    if success:
        con.execute("""UPDATE RainbowTable SET number_of_tries = number_of_tries + 1, successful_tries = successful_tries + 1 WHERE id = ?""", (id,))
    else:
        con.execute("""UPDATE RainbowTable SET number_of_tries = number_of_tries + 1 WHERE id = ?""", (id,))
    con.commit()
    
def fetch_table(id: int):
    """Used to retrieve the table content

    Args:
        id (int): ID of the table
    Returns:
        A list of tuples containing the table content
    """
    cur.execute("SELECT dict_text, name FROM RainbowTable WHERE id = ?", (id,))
    return cur.fetchall()

def get_table_id(RT_name: str):
    """Used to retrieve the table ID

    Args:
        RT_name (str): Name of the table
    Returns:
        The ID of the table
    """
    cur.execute("SELECT id FROM RainbowTable WHERE name = ? AND dict_text = ?", (RT_name, convertToBinaryData(RT_name)))
    return cur.fetchone()[0]
    
def add_password_to_database(hash: str, plaintext: str):
    """Used to add a cracked password to the database

    Args:
        hash (str): Hash of the password
        plaintext (str): Plaintext of the password
    """
    cur.execute("INSERT INTO Password VALUES (?, ?)", (hash, plaintext))
    con.commit()
    
def search_password(hash: str):
    """Used to search for a password in the database

    Args:
        hash (str): Hash of the password
    Returns:
        The plaintext of the password
    """
    cur.execute("SELECT plaintext FROM Password WHERE hash = ?", (hash,))
    return cur.fetchone()
    
def check_name(name: str):
    """Used to check if a table name already exists in the database

    Args:
        name (str): Name of the table
    Returns:
        The name of the table
    """
    cur.execute("SELECT name FROM RainbowTable WHERE name = ?", (name,))
    return cur.fetchone()

def load_all_tables():
    """Used to retrieve all the tables in the database

    Returns:
        A list of tuples containing the information about the tables
    """
    cur.execute("SELECT name, password_length_min, password_length_max, hashing_alg, number_of_tries, successful_tries, id, chain_len, reduction_function FROM RainbowTable")
    return cur.fetchall()

def select_table(id: int):
    """Used to retrieve information about a specific table

    Args:
        id (int): ID of the table
    Returns:
        A list of tuples containing the information about the table
    """
    cur.execute("SELECT * FROM RainbowTable WHERE id = ?", (id,))
    return cur.fetchone()

def load_hash_type_tables(alg: str):
    """Used to retrieve all tables of a specific hash type

    Args:
        alg (str): Hashing algorithm
    Returns:
        A list of tuples containing the information about the tables
    """
    cur.execute("SELECT name, password_length_min, password_length_max, hashing_alg, number_of_tries, successful_tries, id, chain_len, reduction_function FROM RainbowTable WHERE hashing_alg = ?", (alg,))
    return cur.fetchall()

def fetch_table_from_id(id: int):
    """Used to retrieve all information from a table of the given ID

    Args:
        id (int): ID of the table
    Returns:
        A list of tuples containing the information about the table
    """
    cur.execute("SELECT * FROM RainbowTable WHERE id = ?", (id,))
    return cur.fetchone()

def del_from_database(id: int):
    """Used to delete a table from the database

    Args:
        id (int): ID of the table
    """
    cur.execute("DELETE FROM RainbowTable WHERE id = ?", (id,))
    con.commit()