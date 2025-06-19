from flask_restful import Resource, reqparse
from model.profile import UserModel, InstituteModel, UserInstituteRelation
from model.profile import ProfileModel
from flask import request
from datetime import datetime
from flask import jsonify
from util import util
from flask_jwt_extended import (jwt_required)
from util.util import jwt_needed
import requests
import json
from util.util import reimagine_api_url_generator
from util.util import generateHashJson
from pylint.pyreverse.utils import PRIVATE
from flask_jwt_extended.utils import get_jwt_identity
import decimal

parser = reqparse.RequestParser()
parser.add_argument('email', help='This field cannot be blank', required=True)
parser.add_argument('password', help='This field cannot be blank', required=True)

def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)

class InsertUserProfile(Resource):
    @jwt_needed
    def post(self):
        profileRequest = request.json
        account_email = get_jwt_identity()
        existingUser = UserModel.find_by_email(account_email)
        email = {"account_email": account_email}
        profileRequest.update(email)
        if existingUser:
            profileRequest = util.generateHashJson(existingUser.id, profileRequest)
            profile = ProfileModel(
            user_id=existingUser.id,
            first_name=profileRequest['first_name'],
            account_email=account_email,
            middle_name=profileRequest['middle_name'],
            last_name=profileRequest['last_name'],
            address_line_1=profileRequest['address_line_1'],
            address_line_2=profileRequest['address_line_2'],
            zip_code=profileRequest['zip_code'],
            city=profileRequest['city'],
            state=profileRequest['state'],
            country=profileRequest['country'],
            cell_number=profileRequest['cell_number'],
            work_number=profileRequest['work_number'],
            home_number=profileRequest['home_number'],
            hash_id=profileRequest['hash_id'],
            nounce_id=profileRequest['nounce_id'],
            date_created=datetime.now()
           )
            try:
                profile.save_profile()
                return {
                    'Success': True,
                    'Code': 200,
                    'message': 'Profile for {} was saved successfully'.format(account_email)
                    }
            except Exception as e:
                print(e)
                return {
                  'Success': False,
                  'Code': 500,
                  'message': 'Profile {} cannot be saved due to unknow reason.'.format(account_email)
                 }
        else:
            return {
                  'Success': False,
                  'Code': 409,
                  'message': 'Profile {} cannot be saved as user does not exist'.format(account_email)
                 }

class GetUserProfile(Resource):
    @jwt_needed
    def get(self):

        userEmail = get_jwt_identity()
        existingUser = json.loads(ProfileModel.find_by_email_list(userEmail))
        # define pre_hash variable 
        pre_hash = {u"pre_hash": u""}

        if len(existingUser) > 1:
            records_verify = existingUser[0]
            previousRecords = existingUser[1]
            # add pre_hash to records_verify JSON object
            records_verify.update(pre_hash)
            # store current hash into a variable for comparing it later on
            hash_now = records_verify['hash_id']
            # if length is greater than 1 then we need to assign previousRecords hash value to pre_hash of records_verify
            records_verify['pre_hash'] = previousRecords['hash_id']
            # blank out hash value as during construct method it will alway remain blank
            records_verify['hash_id'] = ''

        if len(existingUser) == 1:
            records_verify = existingUser[0]
            # add pre_hash to records_verify JSON object
            records_verify.update(pre_hash)
            # store current hash into a variable for comparing it later on
            hash_now = records_verify['hash_id']
            # blank out hash value as during construct method it will alway remain blank
            records_verify['hash_id'] = ''

        if len(existingUser) == 0:
                return {
                  'Success': False,
                  'Code': 404,
                  'message': 'Profile does not exist for user {}'.format(userEmail)
                 }
        # generate hash value for the last entry    
        hash_value = util.call_hash(records_verify)

        # verfiy existing hash value from db with the newly generated hash value
        if hash_value == hash_now:
            # del hash_id, nounce_id and pre_hash as they are internal 
            del records_verify['hash_id']
            del records_verify['nounce_id']
            del records_verify['pre_hash']
            return jsonify(records_verify)
        else:
            return {
                  'Success': False,
                  'Code': 404,
                  'message': 'Profile {} verification fail'.format(userEmail)
                 }
        
class LinkInstitutes(Resource):
    @jwt_needed
    def get(self):
        userEmail = get_jwt_identity()
        existingUser = UserModel.find_by_email(userEmail)
        try:
            linkedInstitutes = UserInstituteRelation.find_by_user_linked_institutes_list(existingUser.id)
            jsonList = []
            for linkedInstitute in linkedInstitutes:
                tempDict = {}
                print(linkedInstitute.UserInstituteRelation.user_id)
                tempDict['institute_name'] =  linkedInstitute.InstituteModel.institute_name
                tempDict['institute_id'] =  linkedInstitute.UserInstituteRelation.institute_id
                tempDict['user_id'] =  linkedInstitute.UserInstituteRelation.user_id
                jsonList.append(tempDict)
            return jsonify(jsonList)
        except Exception as e:
            print(e)
            return {
              'Success': False,
              'Code': 500,
              'message': 'Error in Linking institute to '.format(userEmail)
             }
    @jwt_needed
    def post(self):
        linkInstitutesRequest = request.json
        userEmail = get_jwt_identity()
        existingUser = UserModel.find_by_email(userEmail)
        institute_id = linkInstitutesRequest['institute_id']
        institute_customer_id = linkInstitutesRequest['institute_customer_id']
        userInstituteRelation = UserInstituteRelation(
            user_id=existingUser.id, institute_id=institute_id, 
            institute_add_date=datetime.now(),
            institute_customer_id=institute_customer_id)
        try:
            UserInstituteRelation.save_user_institute_relation(userInstituteRelation)
            return {
                'Success': True,
                'Code': 200,
                'message': 'Institute has been linked successfully '.format(userEmail)
                }
        except Exception as e:
            print(e)
            return {
              'Success': False,
              'Code': 500,
              'message': 'Error in Linking institute to '.format(userEmail)
             }
        
class Institutes(Resource):
    @jwt_needed
    def post(self):
        try:
            linkInstitutesRequest = request.json
            institute_name = linkInstitutesRequest['institute_name']
            instituteModel = InstituteModel(institute_name=institute_name, date_created=datetime.now())
            InstituteModel.save_institute(instituteModel)
        except Exception as e:
            return {
              'Success': False,
              'Code': 500,
              'message': 'Error in adding institute'
             }
        

# WORK IN PROGRESS: As of now it simply updates address with static data
class InstitutesApis(Resource):
    @jwt_needed
    def post(self):
        account_email = get_jwt_identity()
        profile = ProfileModel.find_latest_by_email(account_email);
        linkInstitutesRequest = request.json
        try:
            linkedInstitutes = UserInstituteRelation.find_by_user_list(profile.user_id, linkInstitutesRequest['institute_id'])
            for linkedInstitute in linkedInstitutes:
    
                data = {
                  "address": {
                    "street_number": profile.address_line_1 +' '+ profile.address_line_2,
                    "street_name": "None",
                    "city": profile.city,
                    "state": profile.state,
                    "zip": profile.zip_code
                  }
                }
                r = requests.put(reimagine_api_url_generator('customers', linkedInstitute.institute_customer_id), json=data)
            return json.loads(r._content)  
        except Exception as e:
            return {
              'Success': False,
              'Code': 500,
              'message': 'Error in adding institute to '
             } 
