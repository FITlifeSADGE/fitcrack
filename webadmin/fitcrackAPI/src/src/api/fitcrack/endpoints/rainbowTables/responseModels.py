from flask_restx import fields
from src.api.apiConfig import api

estimate_model = api.model('Estimate', {
    'time': fields.Integer(readOnly=True, required=False)})