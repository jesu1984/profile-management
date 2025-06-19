from flask_restful import Resource, reqparse
from model.profile import UserModel
from model.profile import LoginHistoryModel
from datetime import datetime
from flask import current_app
from flask_jwt_extended import (create_access_token, create_refresh_token, get_jwt_identity, get_raw_jwt)
from flask_jwt_extended.utils import get_jti, get_jwt_claims
from util.util import jwt_needed, jwt_refresh_token_needed
from config.database import redisDb, jwt

parser = reqparse.RequestParser()
parser.add_argument('email', help='This field cannot be blank', required=True)
parser.add_argument('password', help='This field cannot be blank', required=True)

  
# This is an example of a complex object that we could build
# a JWT from. In practice, this will likely be something
# like a SQLAlchemy instance.
class UserObject:
    def __init__(self, email, roles):
        self.email = email
        self.roles = roles


# Create a function that will be called whenever create_access_token
# is used. It will take whatever object is passed into the
# create_access_token method, and lets us define what custom claims
# should be added to the access token.
@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return {'roles': user.roles}


# Create a function that will be called whenever create_access_token
# is used. It will take whatever object is passed into the
# create_access_token method, and lets us define what the identity
# of the access token should be.
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.email
  
class UserRegistration(Resource):

    def post(self):
        data = parser.parse_args()
    
        if UserModel.find_by_email(data['email']):
            return {
                  'Success': False,
                  'Code': 409,
                  'message': 'User {} already exists'. format(data['email'])
                 }
          
        new_user = UserModel(
            email=data['email'],
            password=UserModel.generate_hash(data['password']),
            date_created=datetime.now()
        )
        try:
            new_user.save_user()
            return {
                  'Success': True,
                  'Code': 200,
                  'message': 'User {} was created'.format(data['email'])
                 }
           
        except Exception as e:
            print(e)
            return {
                  'Success': False,
                  'Code': 500,
                  'message': 'User {} was not created. due to unknow reason.'.format(data['email'])
                 }


class UserLogin(Resource):

    def post(self):
        data = parser.parse_args()
        current_user = UserModel.find_by_email(data['email'])
        if not current_user:
            return {
                  'Success': False,
                  'Code': 404,
                  'message': 'User {} doesn\'t exist'.format(data['email'])
                 }
        
        if UserModel.verify_hash(data['password'], current_user.password):
            login_user = LoginHistoryModel(
                user_id=current_user.id,
                login_date=datetime.now()
            )
            try:
                login_user.save_login_history()
                # Create an example UserObject
                userIdentifier = UserObject(email=data['email'], roles=[])
                access_token = create_access_token(identity=userIdentifier)
                refresh_token = create_refresh_token(identity=userIdentifier)
                access_jti = get_jti(encoded_token=access_token)
                refresh_jti = get_jti(encoded_token=refresh_token)
                redisDb.set(access_jti, 'false', current_app.config['JWT_ACCESS_TOKEN_EXPIRES'] * 1.2)
                redisDb.set(refresh_jti, 'false', current_app.config['JWT_REFRESH_TOKEN_EXPIRES'] * 1.2)
                return {
                    'Success': True,
                    'access_token': access_token,
                    'refresh_token': refresh_token
                    }
            except Exception as e:
                print(e)
                return {
                  'Success': False,
                  'Code': 500,
                  'message': 'User {} cannot login due to unknow reason.'.format(data['email'])
                 }
        else:
            return {
                  'Success': False,
                  'Code': 401,
                  'message': 'Wrong credentials'
                 }

      
class TokenRefresh(Resource):

    @jwt_refresh_token_needed
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class UserLogout(Resource):

    @jwt_needed
    def post(self):
        jti = get_raw_jwt()['jti']
        redisDb.set(jti, 'true', current_app.config['JWT_ACCESS_TOKEN_EXPIRES'] * 1.2)
        return {"msg": "Access token revoked"}
    
