from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.main.db.models import TrainingHistory

# Tworzenie blueprintu dla modułu historii treningów
training_history_bp = Blueprint("training_history_bp", __name__, url_prefix="/api/training-history")

# Endpoint pobierania listy historii treningów
@training_history_bp.route("/list", methods=["GET"])
@jwt_required()
def list_training_history():
    user_id = get_jwt_identity() # Pobranie użytkownika z tokena JWT
    trainings = TrainingHistory.query.filter_by(user_id=user_id).all() # Pobranie wszytskich treningów wykonanych przez użytkownika
    return jsonify([training.to_dict() for training in trainings]), 200