from flask import Blueprint, jsonify, request
from src.main.db.models import Trainer, TrainerRating
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.main.extensions import db

trainers_bp = Blueprint("trainers_bp", __name__, url_prefix="/api/trainers")

@trainers_bp.route("/list", methods=["GET"])
def list_trainers():
    trainers = Trainer.query.all()
    return jsonify([trainer.to_dict() for trainer in trainers]), 200

@trainers_bp.route("/ratings/<trainer_id>", methods=["GET"])
def trainer_ratings(trainer_id):
    ratings = TrainerRating.query.filter_by(trainer_id=trainer_id).all()
    return jsonify([rating.to_dict() for rating in ratings]), 200


@trainers_bp.route("/ratings/<trainer_id>", methods=["POST"])
@jwt_required()
def add_trainer_rating(trainer_id):
    data = request.get_json()
    rating_value = data.get("rating")
    comment = data.get("comment")
    user_id = get_jwt_identity()

    if rating_value is None or comment is None:
        return jsonify({"message": "Rating and comment are required!"}), 400

    existing_rating = TrainerRating.query.filter_by(trainer_id=trainer_id, user_id=user_id).first()
    if existing_rating:
        return jsonify({"message": "You have already rated this trainer!"}), 400

    new_rating = TrainerRating(
        trainer_id=trainer_id,
        user_id=user_id,
        rating=rating_value,
        comment=comment,
        created_at=datetime.utcnow()
    )

    db.session.add(new_rating)
    db.session.commit()

    return jsonify({"message": "Rating added successfully!"}), 201