import os
import pytest
from app import app, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_add_habit(client):
    response = client.post('/habit/add', data={
        'title': 'Читать книги',
        'description': '10 страниц в день'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'\xd0\xa7\xd0\xb8\xd1\x82\xd0\xb0\xd1\x82\xd1\x8c' in response.data  # Проверка кириллицы в ответе
