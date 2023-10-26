#!/usr/bin/env python3
import os
from flask import Flask,make_response,jsonify,request,session
from flask_migrate import Migrate
from models import db,Car,User
from flask_cors import CORS
from flask_restful import Api,Resource
from werkzeug.exceptions import NotFound
from flask_bcrypt import Bcrypt 


app=Flask(__name__)
bcrypt=Bcrypt(app)
api=Api(app) #restful
CORS(app)
app.secret_key=b'\xa8JeWQ\xd2h\x8d\xc6\xaez\x07\xf6)\xfc\xfc'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact=False
migrate=Migrate(app,db,render_as_batch=True)

db.init_app(app)

# @app.before_request
# def check_if_logged_in():
#     if not session['user_id']:
#         return {'error':'unauthorized'},401
    

class CheckSession(Resource):
    def get(self):
        if session.get("user_id"):
            user=User.query.filter(User.id==session["user_id"]).first()
            return user.to_dict(),200
        return {"error": "Resource unavailable"}
    
api.add_resource(CheckSession,'/')

class Index(Resource):
    def get(self):
        response_body= '<h1>Hello World </h1>'
        status=200
        headers={}
        return make_response(response_body,status,headers)
        #redirect
api.add_resource(Index,'/')

class SignUp(Resource):
    def post(self):
        name=request.get_json().get('name')
        password=request.get_json().get('password')

        if name and password:
            new_user=User(name=name)
            new_user.password_hash=password

            db.session.add(new_user)
            db.session.commit()

            session['user_id']=new_user.id
            return new_user.to_dict(),201

api.add_resource(SignUp,'/signup',endpoint='signup')


class login(Resource):
    def post(self):
        name=request.get_json()['name']
        password=request.get_json()['password']

        user=User.query.filter(User.name==name).first()

        if user and user.authenticate(password):
            session['user_id']=user.id
            return user.to_dict(),200
        else:
            return{"error": "user is not authorised to login"}
        
api.add_resource(login, '/login',endpoint='login')

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {'info': 'user logged out successfully'}
        else:
            return {'error': 'unauthorized'}, 401
        
api.add_resource(Logout, "/logout", endpoint="logout")
            

class Users(Resource):
    def get(self,):
        if not session['user_id']:
            return {'error':'unauthorized'},401     

        users=[user.to_dict() for user in User.query.all()]

        response=make_response(jsonify(users),200)
        return response
    
    def post(self):
        name=request.get_json()['name']

        new_user=User(name=name)

        db.session.add(new_user)
        db.session.commit()

        user_dict=new_user.to_dict()
           
        response=make_response(jsonify(user_dict),201)
        
        return response
    

api.add_resource(Users,'/users')


class UserById(Resource):
    def get(self,id):
        user=User.query.filter(User.id==id).first()
        user_dict=user.to_dict()
        response=make_response(jsonify(user_dict),200)
        response.headers['Content-Type']= 'application/json'
        return response
    
    def patch(self,id):
        user=User.query.filter(User.id==id).first()
        for attr in request.form:
            setattr(user, attr, request.form.get(attr))

            db.session.add(user)
            db.session.commit()

            user_dict=user.to_dict()

            response = make_response(jsonify(user_dict),200)

            return response
        
    def delete(self,id):
        user=User.query.filter(User.id==id).first()

        db.session.delete(user)
        db.session.commit()

        response_body = {
            "delete_successful": True,
            "message": "Review deleted."    
        }

        response=make_response(jsonify(response_body),200)
        return response

        
api.add_resource(UserById,'/users/<int:id>')

@app.errorhandler(NotFound)
def handle_not_found(e):
    response= make_response( 'Not Found : The requested resource does not exist', 404)
    return response


if __name__=='__main__':
    app.run(port=5000, debug=True)