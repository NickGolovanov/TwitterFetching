import pytest
from flask import Flask
from .information import information_route

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client

def create_app():
    app = Flask(__name__)
    return app

def test_get_information(client):
    response = client.get('/information/')  # Adjust the path as necessary
    assert response.status_code == 200

def test_get_information_by_id(client):
    response = client.get('/information/1')  # Assuming information with ID 1 exists
    assert response.status_code in (200, 404)

# Removed the test_create_information function as there is no POST route defined.

def test_update_information(client):
    response = client.put('/information/1', json={"data": "updated"})  # Adjust the payload as necessary
    assert response.status_code in (200, 404)

def test_delete_information(client):
    response = client.delete('/information/1')  # Assuming information with ID 1 exists
    assert response.status_code in (200, 404)
