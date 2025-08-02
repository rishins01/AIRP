from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

class Inventory(db.Model):
    vendorId = db.Column(db.Integer, primary_key=True)
    productID = db.Column(db.Integer, primary_key=True)
    productname = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False, default=0)
    vendorId = db.Column(db.Integer, db.ForeignKey('user.id'))

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    productID = db.Column(db.Integer, db.ForeignKey('inventory.productID'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(50), nullable=False)
    times = db.Column(db.DateTime, primary_key=True, default=datetime.datetime.utcnow())

class Cart(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    productID = db.Column(db.Integer, db.ForeignKey('inventory.productID'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)

class RecentlyViewed(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    productID = db.Column(db.Integer, db.ForeignKey('inventory.productID'), primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())

class RecentlySearched(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    query = db.Column(db.String(100), primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())
