from flask import Flask
from flask_cors import CORS
from src.main.extensions import db, jwt, argon2, ACCESS_EXPIRES
from src.main.db.models import User, Trainer, Service, Reservation, TrainingHistory
from src.main.db.dataBaseInitializer import DataBaseInitializer
from src.main.controller.AuthController import auth_bp
from src.main.controller.ReservationsController import reservations_bp
from src.main.controller.ServicesController import services_bp
from src.main.controller.TrainersController import trainers_bp
from src.main.controller.TrainingHistoryController import training_history_bp


def register_extensions(app):
    db.init_app(app)
    jwt.init_app(app)
    argon2.init_app(app)


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@silownia_db:5432/silownia'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 60
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = ACCESS_EXPIRES
    app.config['JWT_ALGORITHM'] = 'ES256'
    app.config['JWT_PUBLIC_KEY'] = open('pub.key', 'r').read()
    app.config['JWT_PRIVATE_KEY'] = open('priv.key', 'r').read()
    app.config['JWT_TOKEN_LOCATION'] = ["cookies"]
    app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True

    register_extensions(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(reservations_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(trainers_bp)
    app.register_blueprint(training_history_bp)


    with app.app_context():
        db.create_all()
        DataBaseInitializer.clear_db()
        DataBaseInitializer.init_db()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)