from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from models import db, Users, Products, Orders, Cart_item, Order_item
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_restful import Api, Resource
from werkzeug.security import check_password_hash, generate_password_hash 
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity
)

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret-key' 
jwt = JWTManager(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cartzone.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

migrate = Migrate(app,db)

db.init_app(app)

api = Api(app)

# Update CORS configuration
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"], supports_credentials=True)

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = Users.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=user.id)
            return jsonify({
                "access_token": access_token,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email
                }
            })
        else:
            return {"error": "Invalid credentials"}, 401

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

        
        required_fields = ['name', 'email', 'password_hash', 'role']
        for field in required_fields:
            if not data.get(field):
                return make_response({'error': f'{field} is required'}, 400)

        if Users.query.filter_by(email=data['email']).first():
            return make_response({'error': 'Email already exists'}, 409)

        hashed_password = generate_password_hash(data['password_hash'])

        new_user = Users(
            name=data['name'],
            email=data['email'],
            password_hash=hashed_password,
            role=data['role']
        )
        db.session.add(new_user)
        db.session.commit()

        return make_response({'message': 'User created', 'data': new_user.to_dict()}, 201)

class UserById(Resource):  
    def get(self, id):
        try:
            user = Users.query.filter_by(id=id).first()
            return make_response(user.to_dict(), 200)
        except Exception as e:
            return make_response(f'id{user.id} not available')
      
    def patch(self, id):
        try:
            data = request.get_json()
            user = Users.query.get(id)
            user.name = data['name']
            user.email = data['email']
            user.password_hash = generate_password_hash(data['password_hash'])
            user.role = data['role']
            db.session.commit()
            return make_response(f'{user.name} updated succesfully')
        except Exception as e:
            return make_response("Invalid inputs")
    
    def delete(self, id):
        try:
            user = Users.query.filter_by(id=id).first()
            db.session.delete(user)
            db.session.commit()
            return make_response(f'{user.name} deleted succesfully')
        except Exception as e:
            return make_response(f'id{user.id} not found')
    
class Product(Resource):
    def get(self):
            products = Products.query.all()
            product_list = [product.to_dict() for product in products]  # convert each user to dict
            return make_response(jsonify(product_list), 200)
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return make_response({'error': 'Admin access only'}, 403)

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
    @jwt_required()
    def get(self, id):
        product = Products.query.get(id)
        if not product:
            return make_response({'error': 'Product not found'}, 404)
        return make_response(product.to_dict(), 200)

    @jwt_required()
    def patch(self, id):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return make_response({'error': 'Admin access only'}, 403)

        data = request.get_json()
        product = Products.query.get(id)
        if not product:
            return make_response({'error': 'Product not found'}, 404)

        try:
            product.name = data.get('name', product.name)
            product.description = data.get('description', product.description)
            product.price = data.get('price', product.price)
            product.stock_quantity = data.get('stock_quantity', product.stock_quantity)
            product.image_url = data.get('image_url', product.image_url)
            db.session.commit()
            return make_response(f'{product.name} updated successfully', 200)
        except Exception:
            return make_response({'error': 'Invalid inputs'}, 400)

    @jwt_required()
    def delete(self, id):
        current_user = get_jwt_identity()
        if current_user['role'] != 'admin':
            return make_response({'error': 'Admin access only'}, 403)

        product = Products.query.get(id)
        if not product:
            return make_response({'error': 'Product not found'}, 404)

        db.session.delete(product)
        db.session.commit()
        return make_response(f'{product.name} deleted successfully', 200)
    
class Order(Resource):
    @jwt_required()
    def get(self):
        orders = Orders.query.all()
        return make_response(jsonify([order.to_dict() for order in orders]), 200)

    @jwt_required()
    def post(self):
        try:
            current_user = get_jwt_identity() 
            data = request.get_json()
              
            new_order = Orders(
                user_id=current_user['id'],
                status=data.get('status', 'processing'),
                total_amount=data['total_amount']
            )
            db.session.add(new_order)
            db.session.flush()  

            for item in data['order_items']:
                order_item = Order_item(
                    order_id=new_order.id,
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    price_at_purchase=item['price_at_purchase']
                )
                db.session.add(order_item)

            db.session.commit()

            return make_response({
                'message': 'Order placed successfully',
                'data': new_order.to_dict()
            }, 201)
        except Exception as e:
            return make_response(f"{order_item.order_id} not found")
        
class OrderById(Resource):  
    def get(self, id):
        order = Order.query.filter_by(id=id).first()
        return make_response(order.to_dict(), 200)
      
    def patch(self, id):
        try:
            data = request.get_json()
            order = Order.query.get(id)
            order.status = data['status']
            order.total_amount = data['total_amount']
            order.user_id = data['user_id']
            db.session.commit()
            return make_response(f'{order.name} updated succesfully')
        except Exception as e:
            return make_response(f"{order.id} not found")
    
    def delete(self, id):
        try:
            order = Order.query.filter_by(id=id).first()
            db.session.delete(order)
            db.session.commit()
            return make_response(f'{order.name} deleted succesfully')
        except Exception as e:
            return make_response(f'id{order.id} not found')

class Cart(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        cart_items = Cart_item.query.filter_by(user_id=current_user['id']).all()
        return make_response(jsonify([item.to_dict() for item in cart_items]), 200)

    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        data = request.get_json()

        new_cart_item = Cart_item(
            user_id=current_user['id'],  # override any spoofed user_id
            product_id=data['product_id'],
            quantity=data['quantity']
        )

        db.session.add(new_cart_item)
        db.session.commit()

        return make_response({'message': 'Item added to cart', 'data': new_cart_item.to_dict()}, 201)

class CartById(Resource):
    @jwt_required()
    def patch(self, id):
        cart_item = Cart_item.query.get_or_404(id)
        data = request.get_json()

        cart_item.quantity = data.get('quantity', cart_item.quantity)

        db.session.commit()
        return make_response(f"Cart item updated successfully", 200)
    
    @jwt_required()
    def delete(self, id):
        current_user = get_jwt_identity()
        cart_item = Cart_item.query.filter_by(id=id, user_id=current_user['id']).first()
        if not cart_item:
            return make_response({"error": "Cart item not found"}, 404)

        db.session.delete(cart_item)
        db.session.commit()
        return make_response(f"Item removed from cart", 200)

class OrderItems(Resource):
    def get(self):
        order_items = Order_item.query.all()
        return make_response(jsonify([item.to_dict() for item in order_items]), 200)

    def post(self):
        data = request.get_json()
        new_order_item = Order_item(
            order_id=data['order_id'],
            product_id=data['product_id'],
            quantity=data['quantity'],
            price_at_purchase=data['price_at_purchase']
        )
        db.session.add(new_order_item)
        db.session.commit()

        return make_response({
            'message': 'Order item added successfully',
            'data': new_order_item.to_dict()
        }, 201)


class OrderItemById(Resource):
    def patch(self, id):
        item = Order_item.query.get_or_404(id)
        data = request.get_json()
        item.quantity = data.get('quantity', item.quantity)
        item.price_at_purchase = data.get('price_at_purchase', item.price_at_purchase)

        db.session.commit()
        return make_response('Order item updated successfully', 200)

    def delete(self, id):
        item = Order_item.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return make_response('Order item deleted successfully', 200)

        
        
        
       

# Routes
api.add_resource(Login, '/login')
api.add_resource(Home, '/')
api.add_resource(User, '/users')
api.add_resource(UserById, '/users/<int:id>')
api.add_resource(Product, '/products')
api.add_resource(ProductById, '/products/<int:id>')
api.add_resource(Order, '/orders')
api.add_resource(OrderById, '/orders/<int:id>')
api.add_resource(Cart, '/cart')
api.add_resource(CartById, '/cart/<int:id>')
api.add_resource(OrderItems, '/orderitem')
api.add_resource(OrderItemById, '/orderitem/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
