from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from models import db, Users, Products, Orders, Cart_item, Order_item
from flask_restful import Api, Resource

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cartzone.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

migrate = Migrate(app,db)

db.init_app(app)

api = Api(app)

class Home(Resource):
    def get(self):
        return make_response("<h1>CartZone>")

class User(Resource):
    def get(self):
        users = Users.query.all()
        users_list = [user.to_dict() for user in users]  # convert each user to dict
        return make_response(jsonify(users_list), 200)
    
    def post(self):
        data = request.get_json()
        name = data['name']
        email = data['email']
        password_hash = data['password_hash']
        role = data['role']
        
        new_user = Users(
            name=name, email=email, password_hash=password_hash, role=role
        )
        db.session.add(new_user)
        db.session.commit()

        return make_response({
            'message': 'User created successfully',
            'data': new_user.to_dict()
        }, 201)
        
class UserById(Resource):  
    def get(self, id):
        user = Users.query.filter_by(id=id).first()
        return make_response(user.to_dict(), 200)
      
    def patch(self, id):
        data = request.get_json()
        user = Users.query.get(id)
        user.name = data['name']
        user.email = data['email']
        user.password_hash = data['password_hash']
        user.role = data['role']
        db.session.commit()
        return make_response(f'{user.name} updated succesfully')
    
    def delete(self, id):
        user = Users.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()
        return make_response(f'{user.name} deleted succesfully')
    
    
class Product(Resource):
    def get(self):
        products = Products.query.all()
        product_list = [product.to_dict() for product in products]  # convert each user to dict
        return make_response(jsonify(product_list), 200)
    
    def post(self):
        data = request.get_json()
        name = data['name']
        description = data['description']
        price = data['price']
        stock_quantity = data['stock_quantity']
        image_url = data['image_url']
        
        new_product = Products(
            name=name, description=description, price=price, stock_quantity=stock_quantity, image_url=image_url
        )
        db.session.add(new_product)
        db.session.commit()

        return make_response({
            'message': 'Product created successfully',
            'data': new_product.to_dict()
        }, 201)
        
class ProductById(Resource):  
    def get(self, id):
        product = Products.query.filter_by(id=id).first()
        return make_response(product.to_dict(), 200)
      
    def patch(self, id):
        data = request.get_json()
        user = Users.query.get(id)
        user.name = data['name']
        user.description = data['description']
        user.price = data['price']
        user.stock_quantity = data['stock_quantity']
        user.image_url = data['image_url']
        db.session.commit()
        return make_response(f'{user.name} updated succesfully')
    
    def delete(self, id):
        product = Products.query.filter_by(id=id).first()
        db.session.delete(product)
        db.session.commit()
        return make_response(f'{product.name} deleted succesfully')


    
        
        
        
       
    
# class 

# Routes
api.add_resource(Home, '/')
api.add_resource(User, '/users')
api.add_resource(UserById, '/users/<int:id>')
api.add_resource(Product, '/products')
api.add_resource(ProductById, '/products/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
