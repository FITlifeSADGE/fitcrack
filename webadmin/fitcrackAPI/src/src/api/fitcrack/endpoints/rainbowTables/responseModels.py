from flask_restx import fields
from src.api.apiConfig import api

estimate_model = api.model('Estimate', {
    'time': fields.Integer(readOnly=True, required=False)})

RTSet_model = api.model('RainbowSet', {
    'id': fields.Integer(readOnly=True, required=False),
    'chain_len': fields.Integer(readOnly=True, required=False),
    'algorithm': fields.String(readOnly=True, required=False),
    'restrictions': fields.String(readOnly=True, required=False),
    'range': fields.String(readOnly=True, required=False),
    'name': fields.String(readOnly=True, required=False),
    'tries': fields.Integer(readOnly=True, required=False),
    'successful': fields.Integer(readOnly=True, required=False),
    'data': fields.String()
})