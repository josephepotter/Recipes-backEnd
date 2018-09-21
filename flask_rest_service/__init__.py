import os, flask_restful
from flask import Flask
from flask_pymongo import PyMongo
from flask import make_response
from flask_cors import CORS
from bson.json_util import dumps
#https://stackoverflow.com/questions/19962699/flask-restful-cross-domain-issue-with-angular-put-options-methods?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
MONGO_URL = os.environ.get('MONGO_URL')
if not MONGO_URL:
    MONGO_URL = "mongodb://localhost:27017/rest";

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config['MONGO_URI'] = MONGO_URL
mongo = PyMongo(app)

def output_json(obj, code, headers=None):
    resp = make_response(dumps(obj), code)
    resp.headers.extend(headers or {})
    return resp

DEFAULT_REPRESENTATIONS = {'application/json': output_json}
api = flask_restful.Api(app)
api.representations = DEFAULT_REPRESENTATIONS

import flask_rest_service.resources
