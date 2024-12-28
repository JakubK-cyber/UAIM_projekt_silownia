import pytest
from flask import json
from app import create_app
from src.main.extensions import db
from src.main.db.models import User, Trainer, TrainingHistory
from datetime import datetime

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client


def test_list_training_history_success(client):
    login_response = client.post('/api/auth/login', json={
            "email": "mariusz.silny@gmail.com",
            "password": "password123"
    })

    atoken = login_response.headers.getlist('Set-Cookie')[0].split(";")[0].split("=")[1]
    x_csrf_token = login_response.headers.getlist('Set-Cookie')[1].split(";")[0].split("=")[1]

    response = client.get('/api/training-history/list', headers={
        "Authorization": f"Bearer {atoken}",
        "X-CSRF-TOKEN": x_csrf_token
    })

    assert response.status_code == 200
    data = response.json
    assert data[0]['details'] == "Trening silowy"
