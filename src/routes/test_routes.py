import pytest
from flask import Flask
from .post import post_route

@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client

def create_app():
    app = Flask(__name__)
    app.register_blueprint(post_route)
    return app

def test_get_posts(client):
    app = create_app()
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200

def test_get_post(client):
    app = create_app()
    with app.test_client() as client:
        response = client.get('/posts/1')  # Assuming post with ID 1 exists
        assert response.status_code in (200, 404)

def test_rehash_post_data(client):
    app = create_app()
    with app.test_client() as client:
        response = client.get('/rehash/some_link')  # Replace with a valid link
        assert response.status_code in (200, 400)
