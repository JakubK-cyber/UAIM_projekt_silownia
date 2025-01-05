from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.main.db.models import Reservation, Trainer, TrainerCalendar
from src.main.extensions import db
from datetime import datetime, timedelta

reservations_bp = Blueprint("reservations_bp", __name__, url_prefix="/api/reservations")

@reservations_bp.route("/book", methods=["POST"])
@jwt_required()
def book_reservation():
    data = request.get_json()
    trainer_id, start_date = data["trainer_id"], data["date"]
    user_id = get_jwt_identity()

    start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    end_date = start_date + timedelta(hours=1)

    if not Trainer.query.get(trainer_id):
        return jsonify({"message": "Trainer not found"}), 404

    existing = Reservation.query.filter(
        Reservation.trainer_id == trainer_id,
        Reservation.date >= start_date,
        Reservation.date < end_date
    ).first()
    if existing:
        return jsonify({"message": "Time slot already booked"}), 400

    reservation = Reservation(user_id=user_id, trainer_id=trainer_id, date=start_date)
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

@reservations_bp.route("/availability/<trainer_id>", methods=["GET"])
@jwt_required(optional=True)
def get_trainer_availability(trainer_id):
    trainer = Trainer.query.get(trainer_id)
    if not trainer:
        return jsonify({"message": "Trainer not found"}), 404

    user_id = get_jwt_identity()
    calendar_entries = TrainerCalendar.query.filter_by(trainer_id=trainer_id).all()
    reservations = Reservation.query.filter_by(trainer_id=trainer_id).all()

    availability = []

    for entry in calendar_entries:
        current_time = entry.available_from
        while current_time < entry.available_to:
            slot_end = current_time + timedelta(minutes=60)

            reservation = next(
                (res for res in reservations if res.date == current_time),
                None
            )
            is_booked = 1 if reservation else 0
            reservation_id = reservation.reservation_id if reservation and reservation.user_id == user_id else None

            availability.append({
                "start": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end": slot_end.strftime("%Y-%m-%d %H:%M:%S"),
                "is_booked": is_booked,
                "reservation_id": reservation_id
            })

            current_time = slot_end

    return jsonify({"availability": availability}), 200