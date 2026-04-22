# tests/test_routes.py
import pytest
import sys
import os

# Добавляем корень проекта в path для импортов
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Проверка health check"""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'

def test_chat_valid_request(client):
    """Проверка валидного запроса к /chat"""
    response = client.post('/chat', 
                          json={'message': 'Test'},
                          content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert 'response' in data
    assert data['source'] in ['llm', 'cache', 'mock']

def test_chat_empty_message(client):
    """Проверка валидации: пустое сообщение"""
    response = client.post('/chat', 
                          json={'message': ''},
                          content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_chat_long_message(client):
    """Проверка валидации: слишком длинное сообщение"""
    response = client.post('/chat', 
                          json={'message': 'x' * 1001},
                          content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'too long' in data['error'].lower()

def test_chat_invalid_json(client):
    """Проверка обработки невалидного JSON"""
    response = client.post('/chat', 
                          data='not json',
                          content_type='application/json')
    assert response.status_code == 400
