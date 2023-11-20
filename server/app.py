#!/usr/bin/env python3

from models import *
from flask import Flask, abort, make_response, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Trains(Resource):
    def get(self):
        try:
            trains = [train.to_dict() for train in Train.query.all()]
            return make_response(trains, 200)
        except ValueError:
            return make_response({'errors' : 'could not fetch train data'}, 400)
        
    def post(self):
        try:
            new_data = request.get_json()
            new_item = Train(**new_data)
            db.session.add(new_item)    
            db.session.commit()
            return make_response(new_item.to_dict(), 200)
        except ValueError:
            db.session.rollback()
            return make_response({'errors' : 'could not create new data'}, 400)

class TrainsById(Resource):
    def get(self, id):
        pass

class Assignments(Resource):
    def get(self):
        try:
            assignments = [assignment.to_dict() for assignment in Assignment.query.all()]
            return make_response(assignments, 200)
        except ValueError:
            return make_response({'errors' : 'could not fetch assignment data'}, 400)
        
    def post(self):
        try:
            new_data = request.get_json()
            new_item = Assignment(**new_data)
            db.session.add(new_item)    
            db.session.commit()
            return make_response(new_item.to_dict(), 200)
        except ValueError:
            db.session.rollback()
            return make_response({'errors' : 'could not create new data'}, 400)

class AssignmentsById(Resource):
    def get(self, id):
        pass

api.add_resource(Trains, '/trains')
api.add_resource(TrainsById, '/trains/<int:id>')
api.add_resource(Assignments, '/assignments')
api.add_resource(AssignmentsById, '/assignments/<int:id>')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
