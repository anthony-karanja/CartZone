# app.py
from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from models import db, Users, Products, Orders, Cart_item, Order_item
from flask_restful import Api, Resource
from flask_cors import CORS
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

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"], supports_credentials=True)

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
                 return {'message': 'Email and password are required'}, 400

        user = Users.query.filter_by(email=email).first()
        if user:
            is_password_correct = user.check_password(password)
            
            if is_password_correct:
                access_token = create_access_token(identity={"id": user.id, "role": user.role, "email": user.email})
              
                return {
                    "message": "Login successful",
                    "access_token": access_token,
                    "user": user.to_dict()
                }, 200
            else:
                return {'message': 'Invalid credentials'}, 401
        else:
            return {'message': 'Invalid credentials'}, 401

class Home(Resource):
    def get(self):
        return make_response("<h1>Welcome to CartZone Backend!</h1>", 200) # More informative message

class User(Resource):
    def get(self):
        users = Users.query.all()
        users_list = [user.to_dict() for user in users]
        return make_response(jsonify(users_list), 200)

    def post(self):
        data = request.get_json()

        required_fields = ['name', 'email', 'password', 'role'] # 'password' as per frontend
        for field in required_fields:
            if not data.get(field):
                return {'error': f'{field} is required'}, 400

        if Users.query.filter_by(email=data['email']).first():
            return {'error': 'Email already exists'}, 409

        try:
            new_user = Users(
                name=data['name'],
                email=data['email'],
                password_hash=data['password'],
                role=data.get('role', 'user') 
            )
            db.session.add(new_user)
            db.session.commit()
            return {'message': 'User created', 'data': new_user.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            import traceback; traceback.print_exc()
            return {'error': 'DB commit failed: ' + str(e)}, 500

class UserById(Resource):
    @jwt_required() 
    def get(self, id):
        current_user_identity = get_jwt_identity()
        user = Users.query.get(id) 

        if not user:
            return {'error': 'User not found'}, 404

        if current_user_identity['id'] != user.id and current_user_identity['role'] != 'admin':
            return {'error': 'Unauthorized access'}, 403

        return user.to_dict(), 200

    @jwt_required()
    def patch(self, id):
        current_user_identity = get_jwt_identity()
        user = Users.query.get(id)

        if not user:
            return {'error': 'User not found'}, 404

        if current_user_identity['id'] != user.id and current_user_identity['role'] != 'admin':
            return {'error': 'Unauthorized access'}, 403

        data = request.get_json()
        try:
            user.name = data.get('name', user.name)
            user.email = data.get('email', user.email)
            if 'password' in data and data['password']:
                user.password_hash = data['password']
            # Only adm
            if 'role' in data and current_user_identity['role'] == 'admin':
                user.role = data['role']
            elif 'role' in data and current_user_identity['role'] != 'admin':
                 return {'error': 'Unauthorized to change role'}, 403

            db.session.commit()
            return {'message': f'{user.name} updated successfully', 'data': user.to_dict()}, 200
        except ValueError as e: 
            db.session.rollback()
            return {'error': str(e)}, 400
        except Exception as e:
            db.session.rollback()
            import traceback; traceback.print_exc()
            return {'error': 'Server error: ' + str(e)}, 500

    @jwt_required() # Pr
    def delete(self, id):
        current_user_identity = get_jwt_identity()
        user = Users.query.get(id)

        if not user:
            return {'error': 'User not found'}, 404

        # Only admin can delete users
        if current_user_identity['role'] != 'admin':
            return {'error': 'Admin access only to delete users'}, 403

        try:
            db.session.delete(user)
            db.session.commit()
            return {'message': f'{user.name} deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Server error during deletion: ' + str(e)}, 500

class Product(Resource):
    def get(self):
        products = Products.query.all()
        return [p.to_dict() for p in products], 200
    

    @jwt_required()
    def post(self):
        print("DEBUG received data:", data)
        print("DEBUG price type:", type(data.get('price')))
        print("DEBUG stock_quantity type:", type(data.get('stock_quantity')))
        current_user_identity = get_jwt_identity()
        if current_user_identity.get('role') != 'admin':
            return {'error': 'Admin access only'}, 403

        data = request.get_json()

        required_fields = ['name', 'description', 'price', 'stock_quantity', 'image_url']
        for field in required_fields:
            if not data.get(field):
                return {'error': f'{field} is required'}, 400

        try:
            price = float(data.get('price', 0))
            stock_quantity = int(data.get('stock_quantity', 0))
            if price < 0 or stock_quantity < 0: 
                return {'error': 'Price and stock quantity cannot be negative'}, 400
        except (ValueError, TypeError) as e:
            return {'error': f'Invalid data type for price or stock_quantity: {e}'}, 422

        try:
            new_product = Products(
                name=data['name'],
                description=data['description'],
                price=price,
                stock_quantity=stock_quantity,
                image_url=data['image_url']
            )
            
            print("DEBUG received data:", data)
            print("DEBUG price type:", type(data.get('price')))
            print("DEBUG stock_quantity type:", type(data.get('stock_quantity')))
            db.session.add(new_product)
            db.session.commit()
            return {'message': 'Product created', 'data': new_product.to_dict()}, 201
        except Exception as e:
            db.session.rollback()
            import traceback; traceback.print_exc()
            return {'error': 'Server error: ' + str(e)}, 500

class ProductById(Resource):
    def get(self, id): # Public endpoint for single product lookup
        product = Products.query.get(id)
        if not product:
            return {'error': 'Product not found'}, 404
        return product.to_dict(), 200

    @jwt_required()
    def patch(self, id):
        current_user_identity = get_jwt_identity()
        if current_user_identity.get('role') != 'admin':
            return {'error': 'Admin access only'}, 403

        data = request.get_json()
        product = Products.query.get(id)
        if not product:
            return {'error': 'Product not found'}, 404

        try:
            if 'name' in data: product.name = data['name']
            if 'description' in data: product.description = data['description']
            if 'price' in data:
                price = float(data['price'])
                if price < 0: return {'error': 'Price cannot be negative'}, 400
                product.price = price
            if 'stock_quantity' in data:
                stock_quantity = int(data['stock_quantity'])
                if stock_quantity < 0: return {'error': 'Stock quantity cannot be negative'}, 400
                product.stock_quantity = stock_quantity
            if 'image_url' in data: product.image_url = data['image_url']

            db.session.commit()
            return {'message': f'{product.name} updated successfully', 'data': product.to_dict()}, 200
        except (ValueError, TypeError) as e:
            db.session.rollback()
            return {'error': f'Invalid data type for price or stock_quantity: {e}'}, 400
        except Exception as e:
            db.session.rollback()
            import traceback; traceback.print_exc()
            return {'error': 'Server error: ' + str(e)}, 500

    @jwt_required()
    def delete(self, id):
        current_user_identity = get_jwt_identity()
        if current_user_identity.get('role') != 'admin':
            return {'error': 'Admin access only'}, 403

        product = Products.query.get(id)
        if not product:
            return {'error': 'Product not found'}, 404

        try:
            db.session.delete(product)
            db.session.commit()
            return {'message': f'{product.name} deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Server error during deletion: ' + str(e)}, 500
    

class Order(Resource):
    @jwt_required()
    def get(self):
        current_user_identity = get_jwt_identity()
        if current_user_identity.get('role') == 'admin':
            orders = Orders.query.all() # Admin can see all orders
        else:
            orders = Orders.query.filter_by(user_id=current_user_identity['id']).all() # User sees their own orders

        # Eager load order_items and their products
        from sqlalchemy.orm import joinedload
        orders = Orders.query.filter(
            (Orders.user_id == current_user_identity['id']) | (current_user_identity.get('role') == 'admin')
        ).options(joinedload(Orders.order_items).joinedload(Order_item.product)).all()


        return jsonify([order.to_dict() for order in orders]), 200

    @jwt_required()
    def post(self):
        current_user_identity = get_jwt_identity()
        user_id = current_user_identity['id']
        data = request.get_json()

        if not data.get('total_amount') is not None and not data.get('order_items'):
             return {'error': 'total_amount and order_items are required'}, 400

        try:
            # Create the order
            new_order = Orders(
                user_id=user_id,
                status=data.get('status', 'processing'),
                total_amount=data['total_amount']
            )
            db.session.add(new_order)
            db.session.flush() # Get the ID for order_items before commit

            # Add order items
            for item_data in data['order_items']:
                product_id = item_data.get('product_id')
                quantity = item_data.get('quantity')
                price_at_purchase = item_data.get('price_at_purchase')

                if not product_id or not quantity or not price_at_purchase:
                    raise ValueError("Product ID, quantity, and price_at_purchase are required for each order item.")

                product = Products.query.get(product_id)
                if not product:
                    raise ValueError(f"Product with ID {product_id} not found for order item.")
                if product.stock_quantity < quantity:
                    raise ValueError(f"Not enough stock for {product.name}. Available: {product.stock_quantity}")

                # Decrement stock quantity
                product.stock_quantity -= quantity

                order_item = Order_item(
                    order_id=new_order.id,
                    product_id=product_id,
                    quantity=quantity,
                    price_at_purchase=price_at_purchase
                )
                db.session.add(order_item)

            db.session.commit()
            return {
                'message': 'Order placed successfully',
                'data': new_order.to_dict()
            }, 201
        except ValueError as e:
            db.session.rollback()
            return {'error': str(e)}, 400
        except Exception as e:
            db.session.rollback()
            import traceback; traceback.print_exc()
            return {'error': 'Server error: ' + str(e)}, 500

class OrderById(Resource):
    @jwt_required() 
    def get(self, id):
        current_user_identity = get_jwt_identity()
        order = Orders.query.filter_by(id=id).options(db.joinedload(Orders.order_items).joinedload(Order_item.product)).first()

        if not order:
            return {'error': 'Order not found'}, 404

        if current_user_identity['id'] != order.user_id and current_user_identity['role'] != 'admin':
            return {'error': 'Unauthorized access to this order'}, 403

        return order.to_dict(), 200

    @jwt_required() 
    def patch(self, id):
        current_user_identity = get_jwt_identity()
        order = Orders.query.get(id)

        if not order:
            return {'error': 'Order not found'}, 404

        # Only admin can update orders
        if current_user_identity['role'] != 'admin':
            return {'error': 'Admin access only to update orders'}, 403

        data = request.get_json()
        try:
            order.status = data.get('status', order.status)
            order.total_amount = data.get('total_amount', order.total_amount)
            # user_id should generally not be changed after order creation
            # order.user_id = data.get('user_id', order.user_id)
            db.session.commit()
            return {'message': f'Order {order.id} updated successfully', 'data': order.to_dict()}, 200
        except Exception as e:
            db.session.rollback()
            import traceback; traceback.print_exc()
            return {'error': 'Server error: ' + str(e)}, 500

    @jwt_required() # Protect this endpoint
    def delete(self, id):
        current_user_identity = get_jwt_identity()
        order = Orders.query.get(id)

        if not order:
            return {'error': 'Order not found'}, 404

        # Only admin can delete orders
        if current_user_identity['role'] != 'admin':
            return {'error': 'Admin access only to delete orders'}, 403

        try:
            db.session.delete(order)
            db.session.commit()
            return {'message': f'Order {order.id} deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Server error during deletion: ' + str(e)}, 500

class Cart(Resource):
    @jwt_required()
    def get(self):
        current_user_identity = get_jwt_identity()
        user_id = current_user_identity['id']
        print(f"DEBUG: Cart GET request by user_id: {user_id}")

        from sqlalchemy.orm import joinedload
        cart_items = Cart_item.query.filter_by(user_id=user_id).options(joinedload(Cart_item.product)).all()
        print(f"DEBUG: Found {len(cart_items)} cart items for user {user_id}")
        
        return jsonify([item.to_dict() for item in cart_items]), 200

    @jwt_required()
    def post(self):
        current_user_identity = get_jwt_identity()
        user_id = current_user_identity['id']
        data = request.get_json()
        print("DEBUG: Received data in /cart POST:", data)

        product_id = data.get('product_id')
        quantity_to_add = data.get('quantity')

        if not product_id or not quantity_to_add or not isinstance(quantity_to_add, int) or quantity_to_add <= 0:
            return {'error': 'Invalid product_id or quantity provided.'}, 400

        product = Products.query.get(product_id)
        if not product:
            return {'error': 'Product not found.'}, 404

        existing_cart_item = Cart_item.query.filter_by(
            user_id=user_id,
            product_id=product_id
        ).first()

        try:
            if existing_cart_item:
                new_total_quantity = existing_cart_item.quantity + quantity_to_add
                if product.stock_quantity < new_total_quantity:
                    return {'error': f'Not enough stock for {product.name}. Max available: {product.stock_quantity}. You currently have {existing_cart_item.quantity} in cart.'}, 400

                existing_cart_item.quantity = new_total_quantity
                db.session.commit()
                # Eager load product for the response
                db.session.refresh(existing_cart_item) # Refresh to get updated state, including product relation if needed
                return {'message': 'Cart item quantity updated successfully.', 'data': existing_cart_item.to_dict()}, 200
            else:
                if product.stock_quantity < quantity_to_add:
                    return {'error': f'Not enough stock for {product.name}. Available: {product.stock_quantity}.'}, 400

                new_cart_item = Cart_item(
                    user_id=user_id,
                    product_id=product_id,
                    quantity=quantity_to_add
                )
                db.session.add(new_cart_item)
                db.session.commit()
                # Eager load product for the response
                db.session.refresh(new_cart_item) # Refresh to get product relation
                return {'message': 'Item added to cart successfully.', 'data': new_cart_item.to_dict()}, 201

        except Exception as e:
            db.session.rollback()
            import traceback; traceback.print_exc()
            return {'error': f'Failed to add/update cart item: {str(e)}'}, 500

class CartById(Resource):
    @jwt_required()
    def patch(self, id):
        current_user_identity = get_jwt_identity()
        user_id = current_user_identity['id']

        cart_item = Cart_item.query.filter_by(id=id, user_id=user_id).first()
        if not cart_item:
            return {"error": "Cart item not found or unauthorized"}, 404

        data = request.get_json()
        new_quantity = data.get('quantity')

        if new_quantity is None or not isinstance(new_quantity, int) or new_quantity <= 0:
            return {'error': 'Quantity must be a positive integer.'}, 400

        product = cart_item.product # Access the related product
        if product.stock_quantity < new_quantity:
            return {'error': f'Not enough stock for {product.name}. Available: {product.stock_quantity}.'}, 400

        try:
            cart_item.quantity = new_quantity
            db.session.commit()
            db.session.refresh(cart_item) # Refresh to ensure product is loaded in to_dict()
            return {"message": "Cart item quantity updated successfully", "data": cart_item.to_dict()}, 200
        except Exception as e:
            db.session.rollback()
            import traceback; traceback.print_exc()
            return {'error': 'Failed to update cart item quantity: ' + str(e)}, 500

    @jwt_required()
    def delete(self, id):
        current_user_identity = get_jwt_identity()
        user_id = current_user_identity['id']

        cart_item = Cart_item.query.filter_by(id=id, user_id=user_id).first()
        if not cart_item:
            return {"error": "Cart item not found or unauthorized"}, 404

        try:
            db.session.delete(cart_item)
            db.session.commit()
            return {"message": "Item removed from cart successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Failed to remove cart item: ' + str(e)}, 500

class OrderItems(Resource):
    @jwt_required() # Assuming order items are sensitive
    def get(self):
        current_user_identity = get_jwt_identity()
        if current_user_identity.get('role') != 'admin':
            return {'error': 'Admin access only'}, 403
        
        order_items = Order_item.query.all()
        return jsonify([item.to_dict() for item in order_items]), 200

    @jwt_required() # Assuming adding individual order items manually is admin-only
    def post(self):
        current_user_identity = get_jwt_identity()
        if current_user_identity.get('role') != 'admin':
            return {'error': 'Admin access only'}, 403

        data = request.get_json()

        required_fields = ['order_id', 'product_id', 'quantity', 'price_at_purchase']
        for field in required_fields:
            if not data.get(field) is not None: # Use 'is not None' for 0 values
                return {'error': f'{field} is required'}, 400
        
        try:
            # Basic validation
            if not Orders.query.get(data['order_id']):
                return {'error': 'Order not found'}, 404
            product = Products.query.get(data['product_id'])
            if not product:
                return {'error': 'Product not found'}, 404
            if product.stock_quantity < data['quantity']:
                return {'error': f'Not enough stock for {product.name}'}, 400

            new_order_item = Order_item(
                order_id=data['order_id'],
                product_id=data['product_id'],
                quantity=data['quantity'],
                price_at_purchase=data['price_at_purchase']
            )
            # Decrement stock when adding an order item directly
            product.stock_quantity -= data['quantity']

            db.session.add(new_order_item)
            db.session.commit()

            return {
                'message': 'Order item added successfully',
                'data': new_order_item.to_dict()
            }, 201
        except ValueError as e:
            db.session.rollback()
            return {'error': str(e)}, 400
        except Exception as e:
            db.session.rollback()
            import traceback; traceback.print_exc()
            return {'error': 'Server error: ' + str(e)}, 500

class OrderItemById(Resource):
    @jwt_required() # Protect these endpoints
    def patch(self, id):
        current_user_identity = get_jwt_identity()
        if current_user_identity.get('role') != 'admin':
            return {'error': 'Admin access only'}, 403

        item = Order_item.query.get(id)
        if not item:
            return {'error': 'Order item not found'}, 404

        data = request.get_json()
        try:
            # Revert old stock, apply new stock for quantity changes
            old_quantity = item.quantity
            new_quantity = data.get('quantity', old_quantity)

            if new_quantity is not None and new_quantity != old_quantity:
                if new_quantity < 0: return {'error': 'Quantity cannot be negative'}, 400
                product = item.product
                if product:
                    stock_diff = new_quantity - old_quantity
                    if product.stock_quantity < stock_diff: # Check if there's enough stock for the increase
                        return {'error': f'Not enough stock for {product.name}'}, 400
                    product.stock_quantity -= stock_diff # Adjust stock
                item.quantity = new_quantity

            if 'price_at_purchase' in data:
                price = data['price_at_purchase']
                if price < 0: return {'error': 'Price at purchase cannot be negative'}, 400
                item.price_at_purchase = price

            db.session.commit()
            return {'message': 'Order item updated successfully', 'data': item.to_dict()}, 200
        except ValueError as e:
            db.session.rollback()
            return {'error': str(e)}, 400
        except Exception as e:
            db.session.rollback()
            import traceback; traceback.print_exc()
            return {'error': 'Server error: ' + str(e)}, 500

    @jwt_required() # Protect these endpoints
    def delete(self, id):
        current_user_identity = get_jwt_identity()
        if current_user_identity.get('role') != 'admin':
            return {'error': 'Admin access only'}, 403

        item = Order_item.query.get(id)
        if not item:
            return {'error': 'Order item not found'}, 404

        try:
            # Revert stock when an order item is deleted
            if item.product:
                item.product.stock_quantity += item.quantity # Return quantity to stock

            db.session.delete(item)
            db.session.commit()
            return {'message': 'Order item deleted successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Server error during deletion: ' + str(e)}, 500
        


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
api.add_resource(OrderItems, '/orderitems') # Changed to plural for consistency
api.add_resource(OrderItemById, '/orderitems/<int:id>') # Changed to plural for consistency
# for rule in app.url_map.iter_rules():
#         print("🔗", rule)
if __name__ == '__main__':
    app.run(port=5555, debug=True)