from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.Text)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Nuevos modelos para el sistema de pedidos de pizza
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    direccion = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    fecha_compra = db.Column(db.Date)
    total = db.Column(db.Float)
    pedidos = db.relationship('DetallePedido', backref='cliente', lazy=True)

class DetallePedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    tamano = db.Column(db.String(20))
    ingredientes = db.Column(db.String(100))
    numero_pizzas = db.Column(db.Integer)
    subtotal = db.Column(db.Float)