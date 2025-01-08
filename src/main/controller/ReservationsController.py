from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.main.db.models import Reservation, Trainer, TrainerCalendar
from src.main.extensions import db
from datetime import datetime, timedelta

# Tworzenie blueprintu dla modułu rezerwacji
reservations_bp = Blueprint("reservations_bp", __name__, url_prefix="/api/reservations")

# Endpoint rezerwacji terminu u trenera
@reservations_bp.route("/book", methods=["POST"])
@jwt_required()  # Wymóg uwierzytelnienia JWT
def book_reservation():
    data = request.get_json()  # Pobranie danych z żądania JSON
    trainer_id, start_date = data["trainer_id"], data["date"]  # Pobranie ID trenera i daty rezerwacji
    user_id = get_jwt_identity()  # Pobranie użytkownika z tokena JWT

    start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")  # Konwersja daty na obiekt datetime
    end_date = start_date + timedelta(hours=1)

    # Sprawdzenie, czy trener istnieje
    if not Trainer.query.get(trainer_id):
        return jsonify({"message": "Trainer not found"}), 404

    # Sprawdzenie, czy termin jest już zarezerwowany
    existing = Reservation.query.filter(
        Reservation.trainer_id == trainer_id,
        Reservation.date >= start_date,
        Reservation.date < end_date
    ).first()
    if existing:
        return jsonify({"message": "Time slot already booked"}), 400

    # Tworzenie nowej rezerwacji
    reservation = Reservation(user_id=user_id, trainer_id=trainer_id, date=start_date)
    db.session.add(reservation)
    db.session.commit()
    return jsonify(reservation.to_dict()), 201

# Endpoint anulowania rezerwacji
@reservations_bp.route("/cancel/<reservation_id>", methods=["DELETE"])
@jwt_required()
def cancel_reservation(reservation_id):
    user_id = get_jwt_identity()  # Pobranie tożsamości użytkownika z tokena JWT
    reservation = Reservation.query.filter_by(reservation_id=reservation_id, user_id=user_id).first()  # Pobranie rezerwacji użytkownika

    # Sprawdzenie, czy rezerwacja istnieje
    if not reservation:
        return jsonify({"message": "Reservation not found"}), 404

    db.session.delete(reservation)  # Usunięcie rezerwacji z bazy danych
    db.session.commit()  # Zatwierdzenie zmian w bazie danych
    return jsonify({"message": "Reservation canceled"}), 200

# Endpoint sprawdzania dostępności trenera
@reservations_bp.route("/availability/<trainer_id>", methods=["GET"])
@jwt_required(optional=True)  # Opcjonalne uwierzytelnienie JWT
def get_trainer_availability(trainer_id):
    trainer = Trainer.query.get(trainer_id)  # Pobranie danych trenera
    if not trainer:
        return jsonify({"message": "Trainer not found"}), 404

    user_id = get_jwt_identity()  # Pobranie tożsamości użytkownika z tokena JWT
    calendar_entries = TrainerCalendar.query.filter_by(trainer_id=trainer_id).all()  # Pobranie wpisów kalendarza trenera
    reservations = Reservation.query.filter_by(trainer_id=trainer_id).all()  # Pobranie wszystkich rezerwacji trenera

    availability = []

    for entry in calendar_entries:
        current_time = entry.available_from
        while current_time < entry.available_to:
            slot_end = current_time + timedelta(minutes=60)

            # Sprawdzenie, czy slot jest zarezerwowany
            reservation = next(
                (res for res in reservations if res.date == current_time),
                None
            )
            is_booked = 1 if reservation else 0  # Flaga oznaczająca, czy slot jest zarezerwowany
            reservation_id = reservation.reservation_id if reservation and reservation.user_id == user_id else None  # ID rezerwacji użytkownika

            # Dodanie informacji o slotach do listy dostępności
            availability.append({
                "start": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end": slot_end.strftime("%Y-%m-%d %H:%M:%S"),
                "is_booked": is_booked,
                "reservation_id": reservation_id
            })

            current_time = slot_end 

    return jsonify({"availability": availability}), 200
