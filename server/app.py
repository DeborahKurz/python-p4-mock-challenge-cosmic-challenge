#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
        scientists = Scientist.query.all()

        response_dict_list = [s.to_dict(rules=('-missions','-planets')) for s in scientists]

        response = make_response(
            jsonify(response_dict_list),
            200,
        )

        return response
    
    def post(self):
        try:
            data = request.get_json()
            scientist = Scientist(
                name=data['name'],
                field_of_study=data['field_of_study']
            )
            print("scientist", scientist)
            db.session.add(scientist)
            db.session.commit()
            
            scientist_id = scientist.id

            response_dict = scientist.to_dict()

            response_dict['id'] = scientist_id
        
            response = make_response(
                jsonify(response_dict),
                201,
            )
            return response
        except Exception as e:
            response_body = {
                "errors": ["validation errors"]
            }

            response = make_response(
                jsonify(response_body),
                400
            )
            return response
api.add_resource(Scientists, '/scientists')


class ScientistsByID(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()

        response_dict = scientist.to_dict()

        response = make_response(
            jsonify(response_dict),
            200,
        )
        return response
    
    def patch(self,id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            try:    
                data = request.get_json()
                scientist.name = data['name']
                scientist.field_of_study = data['field_of_study']

                db.session.commit()

                response_dict = scientist.to_dict()

                response = make_response(
                    jsonify(response_dict),
                    202
                )
                return response
            except Exception as e:
                response_body={
                    "errors": ["validation errors"]
                }

                response = make_response(
                    jsonify(response_body),
                    400
                )
                return response
        else:
            response_dict = {
                "error": "Scientist not found"
            }
            response = make_response(
                jsonify(response_dict),
                404
            )
            return response

    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()

        if scientist:
            db.session.delete(scientist)
            db.session.commit()

            response_dict = {"message": "scientist successfully deleted"}
            response = make_response(
                response_dict,
                204
            )
            return response
        else:
            response_dict = {
                "error": "Scientist not found"
            }
            response = make_response(
                jsonify(response_dict),
                404
            )
            return response
api.add_resource(ScientistsByID, '/scientists/<int:id>')

class Planets(Resource):
    def get(self):
        planets = Planet.query.all()

        response_dict_list = [p.to_dict(rules=('-missions',)) for p in planets]

        response = make_response(
            jsonify(response_dict_list),
            200
        )
        return response
api.add_resource(Planets, '/planets')

class Missions(Resource):
    def get(self):
        missions = Mission.query.all()
        response = [m.to_dict(rules=('-scientist','-planet')) for m in missions]

        return response, 200
    
    def post(self):
        try:
            data = request.get_json()
            new_mission = Mission(
                name=data['name'],
                scientist_id=data['scientist_id'],
                planet_id=data['planet_id']
            )

            db.session.add(new_mission)
            db.session.commit()

            return new_mission.to_dict(), 201
        except Exception:
            response = {
                "errors": ["validation errors"]
            }
            return response, 400

api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)

