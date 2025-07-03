"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from sqlalchemy import select
from models import db, User, People, Planets, Favorites_Planets, Favorites_People
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/people', methods=['GET'])
def handle_get_people():

    all_people = db.session.execute(select(People)).scalars().all()

    response_body = {
        "people": [person.serialize() for person in all_people]
    }

    return jsonify(response_body), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def handle_get_person(people_id):
    person = db.session.get(People, people_id)
    if person is None:
        return jsonify({"error":"Personaje no encontrado"}), 404
    return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def handle_get_planets():

    all_planets = db.session.execute(select(Planets)).scalars().all()
    response_body = {
        "planets": [planet.serialize() for planet in all_planets]
    }

    return jsonify(response_body), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def handle_get_planet(planet_id):
    planet = db.session.get(Planets, planet_id)
    if planet is None:
        return jsonify({"error": "Planeta no encontrado"}), 404
    return jsonify(planet.serialize()), 200

@app.route('/users', methods=['GET'])
def get_all_users():
    all_users = db.session.execute(select(User)).scalars().all()
    reponse_body = {
        "users":[user.serialize() for user in all_users]
    }
    return jsonify(reponse_body), 200

@app.route('/users/favorites/<int:user_id>', methods=['GET'])
def get_user_favorites(user_id):
    fav_planets = db.session.execute(select(Favorites_Planets).where(Favorites_Planets.user_id == user_id)).scalars().all()
    
    fav_people = db.session.execute(select(Favorites_People).where(Favorites_People.user_id== user_id)).scalars().all()
    reponse_body = {
        "favorite_planets": [fav.planet_id for fav in fav_planets],
        "favorite_people": [fav.people_id for fav in fav_people]
    }
    return jsonify(reponse_body), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])  
def add_favorite_planet(planet_id):
    data= request.get_json()
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error":"Falta user_id"}),

    planet = db.session.get(Planets, planet_id)
    if planet is None:
        return jsonify({"error":"Planeta no encontrado"}), 404
    
    favorite_planet = Favorites_Planets(user_id=user_id, planet_id=planet_id)
    db.session.add(favorite_planet)
    db.session.commit()

    return jsonify({"msg":"Planeta añadido a favoritos"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    data = request.get_json()
    user_id= data.get("user_id")
    if not user_id:
        return jsonify({"error": "Falta user_id"}),
    favorite_people = Favorites_People(users_id=user_id, people_id=people_id)
    db.session.add(favorite_people)
    db.session.commit()

    return jsonify({"msg":"Personaje añadido a favoritos"}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    data = request.get_json()
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "Falta user_id"}), 400

    favorite = db.session.execute(select(Favorites_Planets).where(Favorites_Planets.user_id == user_id, Favorites_Planets.planet_id == planet_id)).scalar_one_or_none()

    if favorite is None:
        return jsonify({"error": "Favorito no encontrado"}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Planeta eliminado de favoritos"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    data = request.get.json()
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error":"Falta user_id"}),400
    
    favorite = db.session.execute(select(Favorites_People).where(Favorites_People.user_id==user_id, Favorites_People.people_id ==people_id)).scalar_one_or_none()

    if favorite is None:
        return jsonify({"error":"Favorito no encontrado"}), 404
    
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg":"Personaje eliminado de favoritos"})

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
