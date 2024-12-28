import pytest
from flask import json
from app import create_app
from src.main.extensions import db
from src.main.db.models import User

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
            yield client

def test_register_success(client):
    response = client.post('/api/auth/register', json={
        "name": "John1",
        "surname": "Doe1",
        "password": "S3cureP@ssw0rd",
        "email": "johndoe1@test.com"
    })
    assert response.status_code == 201
    assert response.json == {"message": "Account created successfully."}

def test_register_missing_fields(client):
    response = client.post('/api/auth/register', json={
        "name": "John",
        "surname": "Doe",
        "password": "S3cureP@ssw0rd"
    })
    assert response.status_code == 400
    assert response.json == {"message": "All fields are required."}

def test_register_existing_email(client):
    client.post('/api/auth/register', json={
        "name": "Wojciech",
        "surname": "Jakubowski",
        "password": "S3cureP@ssw0rd",
        "email": "mariusz.silny@gmail.com"
    })
    response = client.post('/api/auth/register', json={
        "name": "Wojciech",
        "surname": "Jakubowski",
        "password": "S3cureP@ssw0rd",
        "email": "mariusz.silny@gmail.com"
    })
    assert response.status_code == 400
    assert response.json == {"message": "User with this email already exists."}

def test_login_success(client):
    response = client.post('/api/auth/login', json={
        "email": "mariusz.silny@gmail.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json["message"] == "Login successful."

def test_login_invalid_credentials(client):
    response = client.post('/api/auth/login', json={
        "email": "invalid@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json == {"message": "Invalid email or password."}

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
