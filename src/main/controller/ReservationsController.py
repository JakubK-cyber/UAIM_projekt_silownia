from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.main.db.models import Reservation, Trainer
from src.main.extensions import db
from datetime import datetime

reservations_bp = Blueprint("reservations_bp", __name__, url_prefix="/api/reservations")

@reservations_bp.route("/book", methods=["POST"])
@jwt_required()
def book_reservation():
    data = request.get_json()
    trainer_id, date = data["trainer_id"], data["date"]
    user_id = get_jwt_identity()

    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    if not Trainer.query.get(trainer_id):
        return jsonify({"message": "Trainer not found"}), 404

    existing = Reservation.query.filter_by(trainer_id=trainer_id, date=date).first()
    if existing:
        return jsonify({"message": "Time slot already booked"}), 400

    reservation = Reservation(user_id=user_id, trainer_id=trainer_id, date=date)
    db.session.add(reservation)
    db.session.commit()
    return jsonify(reservation.to_dict()), 201

@reservations_bp.route("/cancel/<reservation_id>", methods=["DELETE"])
@jwt_required()
def cancel_reservation(reservation_id):
    user_id = get_jwt_identity()
    reservation = Reservation.query.filter_by(reservation_id=reservation_id, user_id=user_id).first()

    if not reservation:
        return jsonify({"message": "Reservation not found"}), 404

    db.session.delete(reservation)
    db.session.commit()
    return jsonify({"message": "Reservation canceled"}), 200