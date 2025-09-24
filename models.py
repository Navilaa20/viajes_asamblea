from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class TucTuc(db.Model):
    __tablename__ = "tuc_tuc"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Viaje(db.Model):
    __tablename__ = "viaje"
    id = db.Column(db.Integer, primary_key=True)
    pasajeros = db.Column(db.Integer, nullable=False)
    observaciones = db.Column(db.String(255))
    tuctuc_id = db.Column(db.Integer, db.ForeignKey("tuc_tuc.id"))
