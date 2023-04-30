import time
import csv
from os import system, name
import pathlib
from settings import RT_DIR
import os

CSV_FIELDNAMES = ['start_point', 'endpoint_hash']

def clear():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

class RainbowTable:
    def __init__(self, hash_func, chain_len, reduction_func, gen_func, alg, restrictions, length_min, length_max):
        self.table = {}
        self.hash_func = hash_func
        self.chain_len = chain_len
        self.gen_func = gen_func
        self.reduction_func = reduction_func
        self.alg = alg
        self.rest = restrictions
        self.len = length_min
        self.len_max = length_max
        
    def gen_table(self, file="table.csv", rows=1000):
        """Used to generate a rainbow table

        Args:
            file (str, optional): Name of the file. Defaults to "table.csv".
            rows (int, optional): Number of rows in the table. Defaults to 1000.
        """
        for i in range(rows):
            start = self.gen_func() # generate a random word to start the chain
            plainText = start
            # apply the hash function and reduction function to the word
            for col in range(self.chain_len):
                hashcode = self.hash_func(plainText.encode('utf-8')).hexdigest()
                plainText = self.reduction_func(hashcode, col)
            # store the start point and the endpoint hash in the table
            self.table[hashcode] = start
        # store the parameters of the table in the table   
        self.table['chain_len'] = self.chain_len
        self.table['alg'] = self.alg.lower()
        self.table['rest'] = self.rest.lower()
        self.table['len'] = self.len
        self.table['len_max'] = self.len_max
        
        # Check if the directory exists, if not create it
        if not pathlib.Path(RT_DIR).exists():
            pathlib.Path(RT_DIR).mkdir(parents=True, exist_ok=True)
        # Create the table file
        with open(os.path.join(RT_DIR, file), 'w') as table:
            writer = csv.DictWriter(table, fieldnames=CSV_FIELDNAMES) 
            writer.writeheader()
            for k, v in self.table.items():
                writer.writerow({CSV_FIELDNAMES[0]: v, CSV_FIELDNAMES[1]: k})
                       
    def recreate_chain(self, hashedPassword, start):
        """Used to traverse the chain and find the password

        Args:
            hashedPassword (str): password hash
            start (str): start point of the chain
        Returns:
            password (str): password if found, None otherwise
        """
        for col in range(self.chain_len):
            hash = self.hash_func(start.encode('utf-8')).hexdigest()
            if hash == hashedPassword:
                return start
            start = self.reduction_func(hash, col)
            
        return None

    def crack(self, hashedPassword):
        """Used to search the table for a hash

        Args:
            hashedPassword (str): password hash
        Returns:
            password (str): password if found, None otherwise
        """
        # search the endpoint column for the hash
        if hashedPassword in self.table:
            traversalResult = self.recreate_chain(hashedPassword, self.table[hashedPassword])
            if traversalResult:
                return traversalResult
        # start applying the reduction function to the hash and search the endpoint column for the result
        for startCol in range(self.chain_len-1, -1, -1):
            candidate = hashedPassword
            for col in range(startCol, self.chain_len):
                candidate = self.hash_func(self.reduction_func(candidate, col-1).encode('utf-8')).hexdigest()
            if candidate in self.table:
                traversalResult = self.recreate_chain(hashedPassword, self.table[candidate])
                if traversalResult:
                    return traversalResult
    
    def load_from_csv(self, filename="RainbowTable.csv"):
        """Used to load table content from a csv file

        Args:
            filename (str, optional): Name of the file. Defaults to "RainbowTable.csv".
        """
        self.table = {}
        if not pathlib.Path(filename).exists():
            print("File not found, please check the path and try again.")
            exit(1)
        with open(filename, 'r') as table:
            reader = csv.DictReader(table)
            for row in reader:
                self.table[row[CSV_FIELDNAMES[1]]] = row[CSV_FIELDNAMES[0]]
                
    def get_chain_len(self):
        return self.table['chain_len']