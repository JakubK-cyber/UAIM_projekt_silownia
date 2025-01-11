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

# Funkcja rejestrująca rozszerzenia Flask, takie jak baza danych, JWT i Argon2
def register_extensions(app):
    db.init_app(app)
    jwt.init_app(app)
    argon2.init_app(app)

# Funkcja tworząca i konfigurująca aplikację Flask
def create_app():
    app = Flask(__name__)
    #CORS(app, resources={r"/*": {"origins": "*"}})
    CORS(app, resources={r"/*": {"origins": "127.0.0.1:5000"}})

    # Konfiguracja aplikacji Flask
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@silownia_db:5432/silownia' # URI bazy danych PostgreSQL
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 60 # Czas wygaśnięcia tokena JWT w sekundach
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Wyłączenie śledzenia zmian SQLAlchemy
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = ACCESS_EXPIRES # Ustawienie czasu wygaśnięcia tokena JWT
    app.config['JWT_ALGORITHM'] = 'ES256' # Algorytm używany do podpisywania tokenów JWT
    app.config['JWT_PUBLIC_KEY'] = open('pub.key', 'r').read() # Odczyt klucza publicznego z pliku
    app.config['JWT_PRIVATE_KEY'] = open('priv.key', 'r').read() # Odczyt klucza prywatnego z pliku
    app.config['JWT_TOKEN_LOCATION'] = ["cookies"] # Lokalizacja tokena JWT (w ciasteczkach)
    app.config['JWT_ACCESS_COOKIE_PATH'] = '/' # Ścieżka dla ciasteczek z tokenem JWT
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True # Włączenie ochrony CSRF dla ciasteczek JWT

    # Rejestracja rozszerzeń z aplikacją
    register_extensions(app)

    # Rejestracja blueprintów (modułów) z aplikacją
    app.register_blueprint(auth_bp)
    app.register_blueprint(reservations_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(trainers_bp)
    app.register_blueprint(training_history_bp)

    # Tworzenie bazy danych i inicjalizacja danych
    with app.app_context():
        db.create_all()
        DataBaseInitializer.clear_db()
        DataBaseInitializer.init_db()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
