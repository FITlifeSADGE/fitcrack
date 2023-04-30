# import argparse
# import sys

from src.api.fitcrack.argumentsParser import pagination
from flask_restx import reqparse

# parses arguments for table generation time estimate
rainbowTables_estimateparser = reqparse.RequestParser()
rainbowTables_estimateparser.add_argument('chain_len', type=int, required=True)
rainbowTables_estimateparser.add_argument('chain_num', type=int, required=True)
rainbowTables_estimateparser.add_argument('algorithm', type=int, required=True)
rainbowTables_estimateparser.add_argument('charset', type=str, required=True)
rainbowTables_estimateparser.add_argument('max_len', type=int, required=True)

# parses arguments for table generation
rainbowTables_generateparser = reqparse.RequestParser()
rainbowTables_generateparser.add_argument('length_min', type=int, required=True)
rainbowTables_generateparser.add_argument('length_max', type=int, required=True)
rainbowTables_generateparser.add_argument('restrictions', type=str, required=True)
rainbowTables_generateparser.add_argument('algorithm', type=int, required=True)
rainbowTables_generateparser.add_argument('columns', type=int, required=True)
rainbowTables_generateparser.add_argument('rows', type=int, required=True)
rainbowTables_generateparser.add_argument('filename', type=str, required=True)

# parses arguments for retrieving tables of specific hash type
rainbowTables_loadparser = reqparse.RequestParser()
rainbowTables_loadparser.add_argument('code', type=int, required=True)
