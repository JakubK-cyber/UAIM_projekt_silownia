import pytest
from flask import json
from app import create_app
from src.main.extensions import db
from src.main.db.models import User

# Fixture dla klienta testowego Flask, który jest używany do wysyłania żądań HTTP do aplikacji
@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
            yield client

# Test dla pomyślnej rejestracji użytkownika
def test_register_success(client):
    response = client.post('/api/auth/register', json={
        "name": "Julia",
        "surname": "Szeremta",
        "password": "ABC123qwer",
        "email": "julka@gmail.com"
    })
    assert response.status_code == 201
    assert response.json == {"message": "Account created successfully."}

# Test dla rejestracji z brakującymi polami
def test_register_missing_fields(client):
    response = client.post('/api/auth/register', json={
        "name": "Kamil",
        "surname": "Stoch",
        "password": "BezpieczneDlugieHaslo"
    })
    assert response.status_code == 400
    assert response.json == {"message": "All fields are required."}

# Test dla rejestracji z istniejącym adresem email
def test_register_existing_email(client):
    response = client.post('/api/auth/register', json={
        "name": "Wojciech",
        "surname": "Jakubowski",
        "password": "S3cureP@ssw0rd",
        "email": "mariusz.silny@gmail.com"
    })
    assert response.status_code == 400
    assert response.json == {"message": "User with this email already exists."}

# Test dla pomyślnego logowania
def test_login_success(client):
    response = client.post('/api/auth/login', json={
        "email": "mariusz.silny@gmail.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json["message"] == "Login successful."

# Test dla logowania z niepoprawnymi danymi
def test_login_invalid_credentials(client):
    response = client.post('/api/auth/login', json={
        "email": "invalid@gmail.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json == {"message": "Invalid email or password."}

# Test dla pomyślnego wylogowania
def test_logout(client):
    login_response = client.post('/api/auth/login', json={
        "email": "mariusz.silny@gmail.com",
        "password": "password123"
    })

    atoken = login_response.headers.getlist('Set-Cookie')[0].split(";")[0].split("=")[1]
    x_csrf_token = login_response.headers.getlist('Set-Cookie')[1].split(";")[0].split("=")[1]
    response = client.post('/api/auth/logout', headers={
        "Authorization": f"Bearer {atoken}",
        "X-CSRF-TOKEN": x_csrf_token
    })
    print(response.text)
    assert response.status_code == 200
    assert response.json == {"message": "Logout successful."}

# Test dla odświeżenia tokenu
def test_refresh_token(client):
    login_response = client.post('/api/auth/login', json={
        "email": "mariusz.silny@gmail.com",
        "password": "password123"
    })
    atoken = login_response.headers.getlist('Set-Cookie')[0].split(";")[0].split("=")[1]
    x_csrf_token = login_response.headers.getlist('Set-Cookie')[3].split(";")[0].split("=")[1]
    response = client.post('/api/auth/token/refresh', headers={
        "Authorization": f"Bearer {atoken}",
        "X-CSRF-TOKEN": x_csrf_token
    })
    assert response.status_code == 200
    assert response.json == {"message": "Token refreshed."}
