from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # admin o reportador

class TucTuc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    placa = db.Column(db.String(15), unique=True, nullable=False)
    qr_token = db.Column(db.String(200), unique=True, nullable=False)

class Viaje(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tuctuc_id = db.Column(db.Integer, db.ForeignKey('tuc_tuc.id'))
    pasajeros = db.Column(db.Integer, nullable=False)
    observaciones = db.Column(db.String(200))
    fecha = db.Column(db.DateTime, server_default=db.func.now())
