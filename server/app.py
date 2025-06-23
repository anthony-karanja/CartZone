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
api.add_resource(Home, '/')




if __name__ == '__main__':
    app.run(port=5555, debug=True)
