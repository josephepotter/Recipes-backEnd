import json, flask_restful
import hashlib
from flask import request, abort
from flask_restful import reqparse
from flask_rest_service import app, api, mongo
from cryptography.fernet import Fernet
from bson.objectid import ObjectId

######## Config Variables ######################################################

key = b'W9b1PN9ue6jHi1s7m-fluRMQVk2RHXsDJsl8mT_jebw='
cipher_suite = Fernet(key)

######## BASE CLASSES ##########################################################

class RecipeList(flask_restful.Resource):
    def __init__(self, *args, **kwargs):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('recipe', type=str)
        super(RecipeList, self).__init__()
    def post(self):
        args = self.parser.parse_args()
        if not args['recipe']:
            abort(400)
        recipe = json.loads(args['recipe'])
        recipe["user"] = cipher_suite.decrypt(recipe["user"].encode()).decode()
        print(recipe["user"]);
        id =  mongo.db.recipes.insert(recipe)
        return mongo.db.recipes.find_one({"_id": id})
        abort(400)

class RecipeFromUser(flask_restful.Resource):
    def get(self, token):
        decrypted_username  = cipher_suite.decrypt(token.encode()).decode()
        return [x for x in mongo.db.recipes.find({'user': decrypted_username})]

class RecipeFromId(flask_restful.Resource):
    def get(self, id, token):
        decrypted_username  = cipher_suite.decrypt(token.encode()).decode()
        recipe = mongo.db.recipes.find_one_or_404({"_id": id})
        if recipe.user == decrypted_username:
            return recipe
        else:
            abort(404)

class UserList(flask_restful.Resource):
    def __init__(self, *args, **kwargs):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('user', type=str)
        super(UserList, self).__init__()
    def post(self):
        args = self.parser.parse_args()
        if not args['user']:
            abort(400)
        user = json.loads(args['user'])
        print(user);
        user["password"] = hashlib.sha224(user["password"].encode('utf-8')).hexdigest()
        users = mongo.db.users.find({"username": user["username"]})
        if users.count() > 0:
            return {'success':False, 'message':"That username is already in use"}
        id =  mongo.db.users.insert(user)
        cookie = cipher_suite.encrypt(user["username"].encode())
        return {'success':True, 'message':cookie.decode()};

class Login(flask_restful.Resource):
    def __init__(self, *args, **kwargs):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('user', type=str)
        super(Login, self).__init__()
    def post(self):
        args = self.parser.parse_args()
        if not args['user']:
            abort(400)
        user = json.loads(args['user'])
        user["password"] = hashlib.sha224(user["password"].encode('utf-8')).hexdigest()
        databaseUser = mongo.db.users.find({"username": user["username"]})
        if databaseUser.count() < 1:
            return {'success':False, 'message':"Invalid Username"}
        if databaseUser[0]["password"] == user["password"]:
            cookie = cipher_suite.encrypt(user["username"].encode())
            return {'success':True, 'message':cookie.decode()}
        else:
            return {'success':False, 'message':"Invalid Password"}



######## API ENDPOINTS #########################################################

api.add_resource(RecipeList, '/recipes/')
api.add_resource(RecipeFromUser, '/recipes/user/<token>')
api.add_resource(RecipeFromId, '/recipesid/<id>/<token>')
api.add_resource(UserList, '/users/')
api.add_resource(Login, '/login/')
