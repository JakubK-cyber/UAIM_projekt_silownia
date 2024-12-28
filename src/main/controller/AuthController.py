from flask import request, jsonify, Blueprint
from src.main.extensions import db, jwt, jwt_redis_blocklist, ACCESS_EXPIRES
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies, get_jwt
)
from src.main.db.models import User

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name = data.get('name')
    surname = data.get('surname')
    password = data.get('password')
    email = data.get('email')

    if not all([email, name, surname, password]):
        return jsonify({"message": "All fields are required."}), 400

    if db.session.query(User).filter_by(email=email).first():
        return jsonify({"message": "User with this email already exists."}), 400

    user = User(email=email, name=name, surname=surname)

    if not user.validate_email():
        return jsonify({"message": "Invalid email format."}), 400

    user.set_password(password)
    db.session.add(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error creating account."}), 500

    return jsonify({"message": "Account created successfully."}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"message": "Email and password are required."}), 400

    user = db.session.query(User).filter_by(email=email).first()
    if not user or not user.verify_password(password):
        return jsonify({"message": "Invalid email or password."}), 401

    access_token = create_access_token(identity=user.user_id)
    refresh_token = create_refresh_token(identity=user.email)

    response = jsonify({"message": "Login successful."})
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response, 200

@jwt.token_in_blocklist_loader
def is_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jwt_redis_blocklist.get(jti) is not None

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)
    response = jsonify({"message": "Logout successful."})
    unset_jwt_cookies(response)
    return response, 200

@auth_bp.route("/token/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    response = jsonify({"message": "Token refreshed."})
    set_access_cookies(response, access_token)

    return response, 200

@auth_bp.route("/token/revoke/refresh", methods=["POST"])
@jwt_required(refresh=True)
def revoke_refresh_token():
    jti = get_jwt()["jti"]
    jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)
    return jsonify({"message": "Refresh token revoked."}), 200