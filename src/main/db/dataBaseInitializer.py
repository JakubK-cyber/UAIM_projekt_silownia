from src.main.extensions import db, argon2
from datetime import datetime
from uuid import uuid4
from sqlalchemy import text
from email_validator import validate_email, EmailNotValidError
from src.main.db.models import User, Trainer, Service, Reservation, TrainingHistory, TrainerRating, user_service
from sqlalchemy.dialects.postgresql import UUID


class DataBaseInitializer:
    @staticmethod
    def init_db():
        # Check if the database is already initialized to avoid adding data again
        if User.query.first():
            print("Database is already initialized.")
            return

        try:
            # Create sample users
            user1 = User(name='Mariusz', surname='Pudzianowski', email='mariusz.silny@gmail.com', phone_number='323786789')
            user1.set_password('password123')

            user2 = User(name='Jan', surname='Blachowicz', email='janek.waleczny@gmail.com', phone_number='963554321')
            user2.set_password('securepassword456')

            # Create sample trainers
            trainer1 = Trainer(name='Anna', surname='Lewandowska', expertise='Lubie cwiczyc')
            trainer2 = Trainer(name='Ewa', surname='Chodakowska', expertise='Cwicz duzo')

            db.session.add_all([user1, user2, trainer1, trainer2])
            db.session.commit()

            # Create sample services
            service1 = Service(name='Trening personalny', description='trening poprzez zabawe, duzo gier', price=50.0)
            service2 = Service(name='Yoga', description='Cwiczenia z Yogi dla kazdego', price=30.0)

            # Create sample reservations
            reservation1 = Reservation(user_id=user1.user_id, trainer_id=trainer1.trainer_id, date=datetime.utcnow(), status='scheduled')
            reservation2 = Reservation(user_id=user2.user_id, trainer_id=trainer2.trainer_id, date=datetime.utcnow(), status='completed')

            # Create sample training histories
            training_history1 = TrainingHistory(user_id=user1.user_id, trainer_id=trainer1.trainer_id, date=datetime.utcnow(), details='Trening silowy')
            training_history2 = TrainingHistory(user_id=user2.user_id, trainer_id=trainer2.trainer_id, date=datetime.utcnow(), details='Yoga dla rozciagliwych')

            # Create sample trainer ratings
            rating1 = TrainerRating(trainer_id=trainer1.trainer_id, user_id=user1.user_id, rating=5, comment='Super zajecia', created_at=datetime.utcnow())
            rating2 = TrainerRating(trainer_id=trainer2.trainer_id, user_id=user2.user_id, rating=4, comment='Prawie idealnie.', created_at=datetime.utcnow())

            # Add sample data to the session
            db.session.add_all([service1, service2, reservation1, reservation2, training_history1, training_history2, rating1, rating2])

            # Add relationships between users and services
            user1.services.append(service1)
            user2.services.append(service2)

            # Commit changes to the database
            db.session.commit()
            print("Database has been initialized with sample data.")
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred while initializing the database: {e}")

    @staticmethod
    def clear_db():
        try:
            # Usuń powiązania w tabeli pośredniej user_service
            db.session.query(user_service).delete()

            # Usuń rekordy z powiązanych tabel
            db.session.query(TrainerRating).delete()
            db.session.query(TrainingHistory).delete()
            db.session.query(Reservation).delete()

            # Teraz można bezpiecznie usunąć użytkowników
            db.session.query(User).delete()
            db.session.query(Trainer).delete()
            db.session.query(Service).delete()

            # Commit changes to the database
            db.session.commit()
            print("Database has been cleared.")
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred while clearing the database: {e}")
