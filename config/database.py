from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended.jwt_manager import JWTManager
import redis
from _datetime import timedelta

POSTGRES = {
    'user': 'drrqrnfjgrnueb',
    'pw': '5e7b37a552857bb8702b98fb8baf61267c78eb16df375bd327fc777a052e8781',
    'db': 'dar5r83oh78jf8',
    'host': 'ec2-54-197-239-115.compute-1.amazonaws.com',
    'port': '5432',
 }
ACCESS_EXPIRES = timedelta(minutes=15)
REFRESH_EXPIRES = timedelta(days=180)

db = SQLAlchemy()
redisDb = redis.StrictRedis(host='ec2-3-89-95-131.compute-1.amazonaws.com',port=29159, password='pc12d7f9a5691028a528b28938beb4074f70709c0d3cbde5873362cb22f352149', decode_responses=True)
#redisDb = redis.StrictRedis(host='localhost',port=6379, decode_responses=True)

jwt = JWTManager()

@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    jti = decrypted_token['jti']
    entry = redisDb.get(jti)
    if entry is None:
        return True
    return entry == 'true'
