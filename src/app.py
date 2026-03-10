"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, jsonify, request
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
    all_characters = db.session.execute(select(Characters)).scalars().all()
    results = list(
        map(lambda character: character.serialize(), all_characters))

    return jsonify(results), 200

# Characters / people id
@app.route('/characters/<int:characters_id>', methods=['GET'])
def get_character(characters_id):
    character = db.session.get(Characters, characters_id)

    if character is None:
        return jsonify({"error": "Character not found"}), 404

    return jsonify(character.serialize()), 200

# Planets all
@app.route('/planets', methods=['GET'])
def all_planets():
    all_planets = db.session.execute(select(Planets)).scalars().all()
    results = list(map(lambda planet: planet.serialize(), all_planets))

    return jsonify(results), 200

# Planets id
@app.route('/planets/<int:planets_id>', methods=['GET'])
def get_planet(planets_id):
    planet = db.session.get(Planets, planets_id)

    if planet is None:
        return jsonify({"error": "Planet not found"}), 404

    return jsonify(planet.serialize()), 200

# User
@app.route('/users', methods=['GET'])
def list_users():
    users = db.session.execute(select(User)).scalars().all()

    results = list(map(lambda user: user.serialize(), users))

    return jsonify(results), 200

# Likes
@app.route('/users/favorites', methods=['GET'])
def user_favorites():
    first_user = db.session.execute(select(User)).scalars().first()

    if first_user is None:
        return jsonify({"error": "No users found"}), 404

    user_id = first_user.id

    liked_characters = db.session.execute(
        select(Liked_Characters).where(Liked_Characters.id_user == user_id)
    ).scalars().all()
    characters_result = list(map(
        lambda liked_character: liked_character.character.serialize(), liked_characters))

    liked_planets = db.session.execute(
        select(Liked_Planets).where(Liked_Planets.id_user == user_id)
    ).scalars().all()
    planets_result = list(
        map(lambda liked_planet: liked_planet.planet.serialize(), liked_planets))

    results = {
        "liked_characters": characters_result,
        "liked_planets": planets_result
    }
    return jsonify(results), 200

# Post character (add fav character)
@app.route('/characters', methods=['POST'])
def add_character():
    body = request.get_json()
    if "character_id" not in body or body["character_id"] == "":
        return jsonify({"msg": "character_id is required"}), 400

    first_user = db.session.execute(select(User)).scalars().first()
    liked = Liked_Characters(id_user=first_user.id, id_character=body["character_id"])
    db.session.add(liked)
    db.session.commit()
    return jsonify(liked.character.serialize()), 200

# Post planet (add fav planet)
@app.route('/planets', methods=['POST'])
def add_planet():
    body = request.get_json()
    if "planet_id" not in body or body["planet_id"] == "":
        return jsonify({"msg": "planet_id is required"}), 400

    first_user = db.session.execute(select(User)).scalars().first()
    liked = Liked_Planets(id_user=first_user.id, id_planet=body["planet_id"])
    db.session.add(liked)
    db.session.commit()
    return jsonify(liked.planet.serialize()), 200

# Delete fav character
@app.route('/characters/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    first_user = db.session.execute(select(User)).scalars().first()
    liked = db.session.execute(
        select(Liked_Characters).where(
            Liked_Characters.id_user == first_user.id,
            Liked_Characters.id_character == character_id
        )
    ).scalars().first()
    if liked is None:
        return jsonify({"msg": "Character not found"}), 404
    db.session.delete(liked)
    db.session.commit()
    response_body = {"msg": "Character " + str(character_id) + " deleted."}
    return jsonify(response_body), 200

# Delete fav planet
@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    first_user = db.session.execute(select(User)).scalars().first()
    liked = db.session.execute(
        select(Liked_Planets).where(
            Liked_Planets.id_user == first_user.id,
            Liked_Planets.id_planet == planet_id
        )
    ).scalars().first()
    if liked is None:
        return jsonify({"msg": "Planet not found"}), 404
    db.session.delete(liked)
    db.session.commit()
    response_body = {"msg": "Planet " + str(planet_id) + " deleted."}
    return jsonify(response_body), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
