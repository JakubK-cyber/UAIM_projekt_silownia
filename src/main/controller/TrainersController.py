from flask import Blueprint, jsonify, request
from src.main.db.models import Trainer, TrainerRating
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.main.extensions import db

# Tworzenie blueprintu dla modułu trenerów
trainers_bp = Blueprint("trainers_bp", __name__, url_prefix="/api/trainers")

# Endpoint pobierania listy wszystkich trenerów
@trainers_bp.route("/list", methods=["GET"])
def list_trainers():
    trainers = Trainer.query.all()  # Pobranie wszystkich trenerów z bazy danych
    return jsonify([trainer.to_dict() for trainer in trainers]), 200  # Zwrócenie listy trenerów w formacie JSON

# Endpoint pobierania ocen dla danego trenera
@trainers_bp.route("/ratings/<trainer_id>", methods=["GET"])
def trainer_ratings(trainer_id):
    ratings = TrainerRating.query.filter_by(trainer_id=trainer_id).all()  # Pobranie wszystkich ocen dla danego trenera
    return jsonify([rating.to_dict() for rating in ratings]), 200  # Zwrócenie listy ocen w formacie JSON

# Endpoint dodawania nowej oceny dla trenera
@trainers_bp.route("/ratings/<trainer_id>", methods=["POST"])
@jwt_required()
def add_trainer_rating(trainer_id):
    data = request.get_json()  # Pobranie danych z żądania JSON
    rating_value = data.get("rating")  # Pobranie wartości oceny
    comment = data.get("comment")  # Pobranie komentarza
    user_id = get_jwt_identity()  # Pobranie użytkownika z tokena JWT

    # Sprawdzenie, czy podano wartość oceny i komentarz
    if rating_value is None or comment is None:
        return jsonify({"message": "Rating and comment are required!"}), 400

    # Sprawdzenie, czy użytkownik już ocenił tego trenera
    existing_rating = TrainerRating.query.filter_by(trainer_id=trainer_id, user_id=user_id).first()
    if existing_rating:
        return jsonify({"message": "You have already rated this trainer!"}), 400

    # Tworzenie nowej oceny dla trenera
    new_rating = TrainerRating(
        trainer_id=trainer_id,
        user_id=user_id,
        rating=rating_value,
        comment=comment,
        created_at=datetime.utcnow()  # Ustawienie daty utworzenia na bieżący czas UTC
    )

    db.session.add(new_rating)
    db.session.commit()

    return jsonify({"message": "Rating added successfully!"}), 201  # Zwrócenie potwierdzenia dodania oceny
