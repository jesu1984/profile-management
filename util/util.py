import hashlib
import json
from json import dumps, loads
from config.database import jwt
from config.database import redisDb
from model.profile import ProfileModel

from flask_jwt_extended.view_decorators import verify_jwt_refresh_token_in_request, \
    verify_jwt_in_request
from functools import wraps
import random
from config.config import REIMAGINE_BANK_SANDBOX_API_URL, \
    REIMAGINE_BANK_SANDBOX_API_KEY


@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    jti = decrypted_token['jti']
    entry = redisDb.get(jti)
    if entry is None:
        return True
    return entry == 'true'

    
# Generate hash for incoming data
def call_hash(data):
        stgData = json.dumps(data)
        data_sha256 = hashlib.sha256(dumps(loads(stgData), sort_keys=True).encode('utf-8')).hexdigest()
        return data_sha256


# Generate nouce random digit
def call_nounce():
        nounce = "%032x" % random.getrandbits(256)
        return nounce


# Add hash, nouce and pre_hash to incoming request
def data_contruct_new(userPayload):
    nounce = {"nounce_id": u""}
    hash = {"hash_id": u""}
    pre_hash = {"pre_hash": u""}
    userPayload.update(nounce)
    userPayload.update(hash)
    userPayload.update(pre_hash)
    return userPayload


def jwt_needed(func):

    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as e:
            return {'error': 'access token error: ' + str(e)}, 401

        return func(*args, **kwargs)

    return decorator


def jwt_refresh_token_needed(func):

    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            verify_jwt_refresh_token_in_request()
        except Exception as e:
            return {'error': 'refresh token error' + str(e)}, 401

        return func(*args, **kwargs)

    return decorator


def reimagine_api_url_generator(resource, resourceId = ''):
    url = REIMAGINE_BANK_SANDBOX_API_URL + '/' + resource + '/' + resourceId + '?key=' + REIMAGINE_BANK_SANDBOX_API_KEY
    return url

def generateHashJson(userId, userPayload):
        modifyUserReq = data_contruct_new(userPayload)
        existingHash = ProfileModel.find_by_userId(userId)
        if existingHash:
            modifyUserReq['pre_hash'] = existingHash.hash_id
        else:
            modifyUserReq['pre_hash'] = ""
        # generate nouce 
        modifyUserReq['nounce_id'] = call_nounce()
        # generate hash for incoming event 
        modifyUserReq['hash_id'] = call_hash(modifyUserReq)
        return modifyUserReq
