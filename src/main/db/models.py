from src.main.extensions import db, argon2
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID

# Definicja tabeli pomocniczej dla relacji wiele-do-wielu między użytkownikami a usługami
user_service = db.Table(
    'user_service',
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('users.user_id'), primary_key=True),
    db.Column('service_id', db.Integer, db.ForeignKey('services.service_id'), primary_key=True)
)

# Model użytkownika
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(32), nullable=False)
    surname = db.Column(db.String(32))
    password_hash = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    trainings = db.relationship('TrainingHistory', backref='user', lazy=True)
    ratings = db.relationship('TrainerRating', backref='user', lazy=True)
    services = db.relationship('Service', secondary=user_service, back_populates='users')

    # Ustawianie hasła użytkownika
    def set_password(self, password):
        self.password_hash = argon2.generate_password_hash(password)

     # Weryfikacja hasła użytkownika
    def verify_password(self, password):
        return argon2.check_password_hash(self.password_hash, password)

    # Walidacja adresu email użytkownika
    def validate_email(self):
        try:
            validate_email(self.email)
            return True
        except EmailNotValidError:
            return False

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
            'name': self.name,
            'surname': self.surname,
            'phone_number': self.phone_number,
            'reservations': [reservation.reservation_id for reservation in self.reservations],
            'trainings': [training.training_id for training in self.trainings],
            'ratings': [rating.rating_id for rating in self.ratings],
            'services': [service.service_id for service in self.services]
        }

# Model trenera
class Trainer(db.Model):
    __tablename__ = 'trainers'
    trainer_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = db.Column(db.String(32), nullable=False)
    surname = db.Column(db.String(32), nullable=False)
    expertise = db.Column(db.String(120), nullable=False)
    ratings = db.relationship('TrainerRating', backref='trainer', lazy=True)
    calendar = db.relationship('Reservation', backref='trainer', lazy=True)
    availability = db.relationship('TrainerCalendar', backref='trainer', lazy=True)

    def to_dict(self):
        return {
            'trainer_id': self.trainer_id,
            'name': self.name,
            'surname': self.surname,
            'expertise': self.expertise,
            'ratings': [rating.rating_id for rating in self.ratings],
            'calendar': [reservation.reservation_id for reservation in self.calendar],
            'availability': [entry.availability_id for entry in self.availability]
        }

# Model oceny trenera
class TrainerRating(db.Model):
    __tablename__ = 'trainer_ratings'
    rating_id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('trainers.trainer_id'), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'rating_id': self.rating_id,
            'trainer_id': self.trainer_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at
        }

# Model kalendarza dostępności trenera
class TrainerCalendar(db.Model):
    __tablename__ = 'trainer_calendar'
    availability_id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('trainers.trainer_id'), nullable=False)
    available_from = db.Column(db.DateTime, nullable=False)
    available_to = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            'availability_id': self.availability_id,
            'trainer_id': self.trainer_id,
            'available_from': self.available_from,
            'available_to': self.available_to
        }

# Model usługi
class Service(db.Model):
    __tablename__ = 'services'
    service_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    users = db.relationship('User', secondary=user_service, back_populates='services')

    def to_dict(self):
        return {
            'service_id': self.service_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'users': [user.user_id for user in self.users]
        }

# Model rezerwacji
class Reservation(db.Model):
    __tablename__ = 'reservations'
    reservation_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)
    trainer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('trainers.trainer_id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')

    def to_dict(self):
        return {
            'reservation_id': self.reservation_id,
            'user_id': self.user_id,
            'trainer_id': self.trainer_id,
            'date': self.date,
            'status': self.status
        }

# Model historii treningów
class TrainingHistory(db.Model):
    __tablename__ = 'training_history'
    training_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'), nullable=False)
    trainer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('trainers.trainer_id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    details = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            'training_id': self.training_id,
            'user_id': self.user_id,
            'trainer_id': self.trainer_id,
            'date': self.date,
            'details': self.details
        }