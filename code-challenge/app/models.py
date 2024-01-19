from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Hero(db.Model):
    __tablename__ = 'hero'

    id = db.Column(db.Integer, primary_key=True)

# add any models you may need. 

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Hero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    super_name = db.Column(db.String(255), nullable=False)
    powers = db.relationship('Power', secondary='hero_power', back_populates='heroes')

class Power(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    heroes = db.relationship('Hero', secondary='hero_power', back_populates='powers')

class HeroPower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String(20), nullable=False)
    hero_id = db.Column(db.Integer, db.ForeignKey('hero.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('power.id'), nullable=False)
    hero = db.relationship('Hero', back_populates='powers')
    power = db.relationship('Power', back_populates='heroes')

# app/__init__.py

from flask import Flask
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db)

    with app.app_context():
        from . import routes, models
        db.create_all()

    return app

# app/routes.py

from flask import Flask, jsonify, request
from .models import db, Hero, Power, HeroPower

app = Flask(__name__)

# Routes for GET /heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    heroes_data = [{'id': hero.id, 'name': hero.name, 'super_name': hero.super_name} for hero in heroes]
    return jsonify(heroes_data)

# Routes for GET /heroes/:id
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):
    hero = Hero.query.get(id)
    if hero:
        hero_data = {
            'id': hero.id,
            'name': hero.name,
            'super_name': hero.super_name,
            'powers': [{'id': power.id, 'name': power.name, 'description': power.description} for power in hero.powers]
        }
        return jsonify(hero_data)
    else:
        return jsonify({'error': 'Hero not found'}), 404

# Routes for GET /powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    powers_data = [{'id': power.id, 'name': power.name, 'description': power.description} for power in powers]
    return jsonify(powers_data)

# Routes for GET /powers/:id
@app.route('/powers/<int:id>', methods=['GET'])
def get_power_by_id(id):
    power = Power.query.get(id)
    if power:
        power_data = {'id': power.id, 'name': power.name, 'description': power.description}
        return jsonify(power_data)
    else:
        return jsonify({'error': 'Power not found'}), 404

# Routes for PATCH /powers/:id
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if power:
        data = request.get_json()
        power.description = data['description']
        try:
            db.session.commit()
            return jsonify({'id': power.id, 'name': power.name, 'description': power.description})
        except Exception as e:
            db.session.rollback()
            return jsonify({'errors': ['validation errors']}), 400
    else:
        return jsonify({'error': 'Power not found'}), 404

# Routes for POST /hero_powers
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    hero_power = HeroPower(strength=data['strength'], hero_id=data['hero_id'], power_id=data['power_id'])
    try:
        db.session.add(hero_power)
        db.session.commit()
        return jsonify(get_hero_by_id(data['hero_id']).json)
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': ['validation errors']}), 400

if __name__ == '__main__':
    app.run(debug=True)

