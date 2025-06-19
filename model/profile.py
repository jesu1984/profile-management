from config.database import db
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy import exc
from sqlalchemy.inspection import inspect
import json
from flask.json import jsonify
from flask.wrappers import Response

class UserModel(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    __table_args__ = {'schema': 'profile_management'}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True))
    date_updated = db.Column(db.DateTime(timezone=True))
    
    def save_user(self):
        db.session.add(self)
        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            print(e)
        
    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    # validate hash for the password
    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


class Serializer(object):

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]


class ProfileModel(db.Model, Serializer):
    __tablename__ = 'profile'
    __table_args__ = {'extend_existing': True}
    __table_args__ = {'schema': 'profile_management'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(UserModel.id))  
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    account_email = db.Column(db.String(100), nullable=False)
    address_line_1 = db.Column(db.String(150), nullable=False)
    address_line_2 = db.Column(db.String(150), nullable=False)
    zip_code = db.Column(db.String(25), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    cell_number = db.Column(db.String(20), nullable=False)
    work_number = db.Column(db.String(20), nullable=False)
    home_number = db.Column(db.String(20), nullable=False)
    hash_id = db.Column(db.String(256), nullable=False, unique=True)
    nounce_id = db.Column(db.String(256), nullable=False, unique=True)
    date_created = db.Column(db.DateTime(timezone=True))

    def serialize(self):
        d = Serializer.serialize(self)
        del d['id']
        del d['user_id']
        del d['date_created']
        return d
    
    @classmethod
    def find_by_userId(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(ProfileModel.date_created.desc()).first()
    
    @classmethod
    def find_by_email_list(cls, email):
        try:
            result = cls.query.filter_by(account_email=email).order_by(ProfileModel.date_created.desc()).limit(2).all()
        except exc.SQLAlchemyError as e:
            print(e)
            return result == None
        return json.dumps(ProfileModel.serialize_list(result))  # return cls.query.filter_by(account_email = email).order_by(ProfileModel.date_created.desc()).limit(2)

    @classmethod
    def find_latest_by_email(cls, email):
        try:
            result = cls.query.filter_by(account_email=email).order_by(ProfileModel.date_created.desc()).first()
        except exc.SQLAlchemyError as e:
            print(e)
            return result == None
        return result  # return cls.query.filter_by(account_email = email).order_by(ProfileModel.date_created.desc()).limit(2)

    def save_profile(self):
        db.session.add(self)
        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            print(e)


class InstituteModel(db.Model):
    __tablename__ = 'institute'
    __table_args__ = {'extend_existing': True}
    __table_args__ = {'schema': 'profile_management'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    institute_name = db.Column(db.String(100), unique=True, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True))

    def save_institute(self):
        db.session.add(self)
        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            print(e)

class LoginHistoryModel(db.Model):
    __tablename__ = 'login_history'
    __table_args__ = {'extend_existing': True}
    __table_args__ = {'schema': 'profile_management'}
        
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(UserModel.id))
    login_date = db.Column(db.DateTime(timezone=True))
    logout_date = db.Column(db.DateTime(timezone=True))

    def save_login_history(self):
        db.session.add(self)
        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            print(e)


class UserInstituteRelation(db.Model):
    __tablename__ = 'user_institute_relation'
    __table_args__ = {'extend_existing': True}
    __table_args__ = {'schema': 'profile_management'}

    user_id = db.Column(db.Integer, db.ForeignKey(UserModel.id), primary_key=True)
    institute_add_date = db.Column(db.DateTime(timezone=True))
    institute_id = db.Column(db.Integer, db.ForeignKey(InstituteModel.id), primary_key=True)
    institute_customer_id = db.Column(db.String(100), nullable=False)

    def save_user_institute_relation(self):
        db.session.add(self)
        try:
            db.session.commit()
        except exc.SQLAlchemyError as e:
            print(e)
            raise e
    @classmethod
    def find_by_user_linked_institutes_list(cls, userId):
        try:
            result = db.session.query(UserInstituteRelation, InstituteModel).filter(UserInstituteRelation.institute_id == InstituteModel.id).filter_by(user_id=userId).all()
        except exc.SQLAlchemyError as e:
            print(e)
            return None
        return result
    
    @classmethod
    def find_by_user_list(cls, userId, InstituteId):
        try:
            result = db.session.query(UserInstituteRelation).filter_by(user_id=userId, institute_id=InstituteId).all()
        except exc.SQLAlchemyError as e:
            print(e)
            return result == None
        return result