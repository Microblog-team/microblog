import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_version_route(client):
    response = client.get('/version')
    assert response.status_code == 200
    assert response.json == {'version': '1.0.0'}