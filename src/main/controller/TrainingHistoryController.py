from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.main.db.models import TrainingHistory

training_history_bp = Blueprint("training_history_bp", __name__, url_prefix="/api/training-history")

@training_history_bp.route("/list", methods=["GET"])
@jwt_required()
def list_training_history():
    user_id = get_jwt_identity()
    trainings = TrainingHistory.query.filter_by(user_id=user_id).all()
    return jsonify([training.to_dict() for training in trainings]), 200