from flask import request, jsonify, Blueprint
from src.main.extensions import db, jwt, jwt_redis_blocklist, ACCESS_EXPIRES
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies, get_jwt
)
from src.main.db.models import User

# Tworzenie blueprintu dla modułu uwierzytelniania
auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")

# Endpoint rejestracji użytkownika
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()  # Pobranie danych z żądania JSON
    name = data.get('name')  # Pobranie imienia użytkownika
    surname = data.get('surname')  # Pobranie nazwiska użytkownika
    password = data.get('password')  # Pobranie hasła użytkownika
    email = data.get('email')  # Pobranie emaila użytkownika

    # Sprawdzenie, czy wszystkie pola są wypełnione
    if not all([email, name, surname, password]):
        return jsonify({"message": "All fields are required."}), 400

    # Sprawdzenie, czy użytkownik z danym emailem już istnieje
    if db.session.query(User).filter_by(email=email).first():
        return jsonify({"message": "User with this email already exists."}), 400

    # Tworzenie nowego użytkownika
    user = User(email=email, name=name, surname=surname)

    # Walidacja formatu emaila
    if not user.validate_email():
        return jsonify({"message": "Invalid email format."}), 400

    # Ustawienie hasła dla użytkownika
    user.set_password(password)
    db.session.add(user)  # Dodanie użytkownika do sesji bazy danych
    try:
        db.session.commit()  # Zatwierdzenie zmian w bazie danych
    except Exception as e:
        db.session.rollback()  # Wycofanie zmian w przypadku błędu
        return jsonify({"message": "Error creating account."}), 500

    return jsonify({"message": "Account created successfully."}), 201

# Endpoint logowania użytkownika
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()  # Pobranie danych z żądania JSON
    email = data.get("email")  # Pobranie emaila użytkownika
    password = data.get("password")  # Pobranie hasła użytkownika

    # Sprawdzenie, czy email i hasło są podane
    if not all([email, password]):
        return jsonify({"message": "Email and password are required."}), 400

    # Wyszukiwanie użytkownika w bazie danych
    user = db.session.query(User).filter_by(email=email).first()
    if not user or not user.verify_password(password):
        return jsonify({"message": "Invalid email or password."}), 401

    # Tworzenie tokenów dostępu i odświeżenia
    access_token = create_access_token(identity=user.user_id)
    refresh_token = create_refresh_token(identity=user.email)

    response = jsonify({"message": "Login successful."})
    set_access_cookies(response, access_token)  # Ustawienie ciasteczek z tokenem dostępu
    set_refresh_cookies(response, refresh_token)  # Ustawienie ciasteczek z tokenem odświeżenia

    return response, 200

# Funkcja sprawdzająca, czy token JWT jest zablokowany
@jwt.token_in_blocklist_loader
def is_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]  # Pobranie identyfikatora tokena (jti)
    return jwt_redis_blocklist.get(jti) is not None  # Sprawdzenie, czy token jest na blockliście

# Endpoint wylogowania użytkownika
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # Pobranie identyfikatora tokena (jti)
    jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)  # Dodanie tokena do blocklisty
    response = jsonify({"message": "Logout successful."})
    unset_jwt_cookies(response)  # Usunięcie ciasteczek JWT
    return response, 200

# Endpoint odświeżenia tokena dostępu
@auth_bp.route("/token/refresh", methods=["POST"])
@jwt_required(refresh=True)  # Wymóg uwierzytelnienia za pomocą tokena odświeżenia
def refresh_token():
    current_user = get_jwt_identity()  # Pobranie tożsamości użytkownika z tokena JWT
    access_token = create_access_token(identity=current_user)  # Tworzenie nowego tokena dostępu

    response = jsonify({"message": "Token refreshed."})
    set_access_cookies(response, access_token)  # Ustawienie ciasteczek z nowym tokenem dostępu

    return response, 200

# Endpoint unieważnienia tokena odświeżenia
@auth_bp.route("/token/revoke/refresh", methods=["POST"])
@jwt_required(refresh=True)  # Wymóg uwierzytelnienia za pomocą tokena odświeżenia
def revoke_refresh_token():
    jti = get_jwt()["jti"]  # Pobranie identyfikatora tokena (jti)
    jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)  # Dodanie tokena odświeżenia do blocklisty
    return jsonify({"message": "Refresh token revoked."}), 200
