"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Characters, Planets, Liked_Characters, Liked_Planets
from sqlalchemy import select

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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

# Characters / people (all)
@app.route('/characters', methods=['GET'])
def all_characters():
    all_characters = db.session.execute(select(characters)).scalars().all()
    results = list(map(lambda character: character.serialize(), all_characters))

    return jsonify(results), 200

# Characters / people id
@app.route('/characters/<int:characters_id>', methods=['GET'])
def characters():
    characters = db.session.execute(select(Characters)).scalars().all()
    results = list(map(lambda character: character.serialize(), characters))

    return jsonify(results), 200

# Planets all
@app.route('/planets', methods=['GET'])
def all_planets():
    all_planets = db.session.execute(select(Planets)).scalars().all()
    results = list(map(lambda planet: planet.serialize(), all_planets))

    return jsonify(results), 200

# Planets id
@app.route('/planets/<int:planets_id>', methods=['GET'])
def planets():
    characters = db.session.execute(select(Characters)).scalars().all()
    results = list(map(lambda character: character.serialize(), characters))

    return jsonify(results), 200

# User
@app.route('/users', methods=['GET'])
def list_users():
    users = db.session.execute(select(User)).scalars().all()
    
    results = list(map(lambda user: user.serialize(), users))
    
    return jsonify(results), 200

# Liked characters + planets per user 
@app.route('/users/favorites', methods=['GET'])
def user_favorites():

    user_id = 1  # for now, should use a jwt (?)
    
    liked_characters = db.session.execute(
        select(Liked_Characters).where(Liked_Characters.id_user == user_id)
    ).scalars().all()
    characters_result = list(map(lambda liked_character: liked_character.character.serialize(), liked_characters))

    liked_planets = db.session.execute(
        select(Liked_Planets).where(Liked_Planets.id_user == user_id)
    ).scalars().all()
    planets_result = list(map(lambda liked_planet: liked_planet.planet.serialize(), liked_planets))

    results = {
        "liked_characters": characters_result,
        "liked_planets": planets_result
    }

    return jsonify(results), 200

"""
Todo:
[POST] /favorite/planet/<int:planet_id> Añade un nuevo planet favorito al usuario actual con el id = planet_id.
[POST] /favorite/people/<int:people_id> Añade un nuevo people favorito al usuario actual con el id = people_id.
[DELETE] /favorite/planet/<int:planet_id> Elimina un planet favorito con el id = planet_id.
[DELETE] /favorite/people/<int:people_id> Elimina un people favorito con el id = people_id
And add a jwt to auth user 
"""


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
