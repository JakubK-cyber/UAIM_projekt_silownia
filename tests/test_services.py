import pytest
from flask import json
from app import create_app
from src.main.extensions import db
from src.main.db.models import Service

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client

# Test dla listy usług
def test_list_services_success(client):
    with client.application.app_context():
        response = client.get('/api/services/list')

        assert response.status_code == 200
        data = response.json
        assert len(data) == 2
        assert data[0]['name'] == 'Trening personalny'
        assert data[1]['name'] == 'Yoga'
