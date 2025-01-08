import pytest
from flask import json
from app import create_app
from src.main.extensions import db
from src.main.db.models import Trainer, TrainerRating

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client

# TEst wypisania listy trenerów
def test_list_trainers_success(client):
        response = client.get('/api/trainers/list')

        assert response.status_code == 200
        data = response.json
        assert len(data) == 2
        assert data[0]['name'] == 'Anna'
        assert data[1]['name'] == 'Ewa'

# Test wypisania oceny trenera
def test_trainer_ratings_success(client):
    with client.application.app_context():
        trainer1 = Trainer.query.filter_by(name="Anna").first().trainer_id

        response = client.get(f'/api/trainers/ratings/{trainer1}')

        assert response.status_code == 200
        data = response.json
        assert len(data) == 1
        assert data[0]['rating'] == 5

# Test dodania nowej oceny trenerowi
def test_trainer_ratings_add_success(client):
    with client.application.app_context():
        login_response = client.post('/api/auth/login', json={
            "email": "janek.waleczny@gmail.com",
            "password": "securepassword456"
        })

        atoken = login_response.headers.getlist('Set-Cookie')[0].split(";")[0].split("=")[1]
        x_csrf_token = login_response.headers.getlist('Set-Cookie')[1].split(";")[0].split("=")[1]
     
        trainer1 = Trainer.query.filter_by(name="Anna").first().trainer_id

        rating_data = {
            "rating": 5,
            "comment": "Great trainer!"
        }

        response = client.post(f'/api/trainers/ratings/{trainer1}', json=rating_data, headers={
            "Authorization": f"Bearer {atoken}",
            "X-CSRF-TOKEN": x_csrf_token
        })

        assert response.status_code == 201
        assert response.json == {"message": "Rating added successfully!"}
