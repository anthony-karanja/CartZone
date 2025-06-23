from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin 
from sqlalchemy.orm import validates

metadata = MetaData()

db = SQLAlchemy(metadata=metadata)

class Users(db.Model, SerializerMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password_hash = db.Column(db.Integer, unique=True)
    role = db.Column(db.String)
    
    orders = db.relationship('Orders', back_populates='users')
    cart_items = db.relationship('Cart_item', back_populates='users')
    
class Products(db.Model, SerializerMixin):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String)
    
    cart_items = db.relationship('Cart_item', back_populates='products')
    
class Orders(db.Model, SerializerMixin):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.String, nullable=False)
    status = db.Column(db.String)
    total_amount = db.Column(db.Float)
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
    
    users = db.relationship('Users', back_populates='orders')
    order_items = db.relationship('Order_item', back_populates='orders')
    
class Cart_item(db.Model, SerializerMixin):
    __tablename__ = 'cart_item'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
    product_id = db.column(db.Integer, db.ForeignKey('products.id'))
    
    users = db.relationship('Users', back_populates='cart_items')
    products = db.relationship('Products', back_populates='cart_items')
    
class Order_item(db.Model, SerializerMixin):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)
    price_at_purchase = db.Column(db.Float)
    product_id = db.column(db.Integer, db.ForeignKey('products.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    
    orders = db.relationship('Orders', back_populates='users')
    products = db.relationship('Products', back_populates='cart_items')
    
   
    
    
