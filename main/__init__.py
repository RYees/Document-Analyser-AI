from flask import jsonify

from ragbackend.main.api import api
from flask_cors import CORS, cross_origin

def init_app(app):
    CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"]}})
    api.init_app(app)
