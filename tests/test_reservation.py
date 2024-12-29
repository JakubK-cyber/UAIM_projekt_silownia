import pytest
from flask import json
from app import create_app
from src.main.extensions import db
from src.main.db.models import User, Trainer, Reservation
from datetime import datetime

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client

def test_book_reservation_success(client):
    with client.application.app_context():
        trainer1 = Trainer.query.filter_by(name="Anna").first().trainer_id

        login_response = client.post('/api/auth/login', json={
            "email": "mariusz.silny@gmail.com",
            "password": "password123"
        })


        atoken = login_response.headers.getlist('Set-Cookie')[0].split(";")[0].split("=")[1]
        x_csrf_token = login_response.headers.getlist('Set-Cookie')[1].split(";")[0].split("=")[1]

        reservation_data = {
            "trainer_id": trainer1,
            "date": "2025-12-28 10:00:00"
        }
        response = client.post('/api/reservations/book', json=reservation_data, headers={
            "Authorization": f"Bearer {atoken}",
            "X-CSRF-TOKEN": x_csrf_token
        })
        assert response.status_code == 201

def test_book_reservation_trainer_not_found(client):
    with client.application.app_context():
        trainer1 = Trainer.query.filter_by(name="Anna").first().trainer_id
        login_response = client.post('/api/auth/login', json={
            "email": "mariusz.silny@gmail.com",
            "password": "password123"
        })

        atoken = login_response.headers.getlist('Set-Cookie')[0].split(";")[0].split("=")[1]
        x_csrf_token = login_response.headers.getlist('Set-Cookie')[1].split(";")[0].split("=")[1]

        reservation_data = {
            "trainer_id": "00000000-0000-0000-0000-0000000003e7", #999 zapisane w UUID
            "date": "2025-12-28 10:00:00"
        }
        response = client.post('/api/reservations/book', json=reservation_data, headers={
            "Authorization": f"Bearer {atoken}",
            "X-CSRF-TOKEN": x_csrf_token
        })
        print(response.text)
        assert response.status_code == 404
        assert response.json == {"message": "Trainer not found"}

def test_book_reservation_time_slot_already_booked(client):
    with client.application.app_context():
        trainer1 = Trainer.query.filter_by(name="Anna").first().trainer_id

        login_response = client.post('/api/auth/login', json={
            "email": "mariusz.silny@gmail.com",
            "password": "password123"
        })

        atoken = login_response.headers.getlist('Set-Cookie')[0].split(";")[0].split("=")[1]
        x_csrf_token = login_response.headers.getlist('Set-Cookie')[1].split(";")[0].split("=")[1]

        reservation_data = {
            "trainer_id": trainer1,
            "date": "2025-11-28 10:00:00"
        }
        client.post('/api/reservations/book', json=reservation_data, headers={
            "Authorization": f"Bearer {atoken}",
            "X-CSRF-TOKEN": x_csrf_token
        })

        response = client.post('/api/reservations/book', json=reservation_data, headers={
            "Authorization": f"Bearer {atoken}",
            "X-CSRF-TOKEN": x_csrf_token
        })
        assert response.status_code == 400
        assert response.json == {"message": "Time slot already booked"}

def test_cancel_reservation_success(client):
    with client.application.app_context():
        trainer1 = Trainer.query.filter_by(name="Anna").first().trainer_id

        user = User.query.filter_by(email="mariusz.silny@gmail.com").first()
        reservation = Reservation(user_id=user.user_id, trainer_id=trainer1, date=datetime.strptime("2024-12-28 10:00:00", "%Y-%m-%d %H:%M:%S"))
        db.session.add(reservation)
        db.session.commit()

        login_response = client.post('/api/auth/login', json={
            "email": "mariusz.silny@gmail.com",
            "password": "password123"
        })

        atoken = login_response.headers.getlist('Set-Cookie')[0].split(";")[0].split("=")[1]
        x_csrf_token = login_response.headers.getlist('Set-Cookie')[1].split(";")[0].split("=")[1]

        response = client.delete(f'/api/reservations/cancel/{reservation.reservation_id}', headers={
            "Authorization": f"Bearer {atoken}",
            "X-CSRF-TOKEN": x_csrf_token
        })
        assert response.status_code == 200
        assert response.json == {"message": "Reservation canceled"}

def test_cancel_reservation_not_found(client):
    login_response = client.post('/api/auth/login', json={
        "email": "mariusz.silny@gmail.com",
        "password": "password123"
    })

    atoken = login_response.headers.getlist('Set-Cookie')[0].split(";")[0].split("=")[1]
    x_csrf_token = login_response.headers.getlist('Set-Cookie')[1].split(";")[0].split("=")[1]

    response = client.delete('/api/reservations/cancel/9999', headers={
        "Authorization": f"Bearer {atoken}",
        "X-CSRF-TOKEN": x_csrf_token
    })
    assert response.status_code == 404
    assert response.json == {"message": "Reservation not found"}
