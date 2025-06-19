from flask import Flask
from flask_restful import Api
from config.database import db
from config.database import jwt
from config.database import POSTGRES, ACCESS_EXPIRES, REFRESH_EXPIRES
from controller import auth as authController
from controller import profile as profileController

def register_extensions(app):
    db.init_app(app) 
    jwt.init_app(app)


def create_app():
    app = Flask(__name__)
    
    # TODO: this config should be set in config file which in config package. I haven;t yet figured out how :)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['JWT_SECRET_KEY'] = 'DoNoTtOuchOurBlOOdySeCret@786110'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = ACCESS_EXPIRES
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = REFRESH_EXPIRES
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
    
    api = Api(app)
    api.add_resource(authController.UserRegistration, '/registration')
    api.add_resource(authController.UserLogin, '/login')
    api.add_resource(authController.UserLogout, '/logout')
    api.add_resource(authController.TokenRefresh, '/refreshTocken')
    
    api.add_resource(profileController.InsertUserProfile, '/insert')
    api.add_resource(profileController.GetUserProfile, '/verify')
    api.add_resource(profileController.Institutes, '/institutes')
    api.add_resource(profileController.LinkInstitutes, '/linkInstitutes')
    api.add_resource(profileController.InstitutesApis, '/updateInstituteAddress')


    register_extensions(app)

    return app


app = create_app()
if __name__ == "__main__":
    app.run()
