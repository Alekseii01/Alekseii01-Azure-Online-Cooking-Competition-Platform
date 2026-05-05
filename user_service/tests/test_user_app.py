import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from datetime import datetime
from user_service.app import app, User, get_db

client = TestClient(app)

@pytest.fixture
def mock_db():
    db = MagicMock()
    app.dependency_overrides[get_db] = lambda: db
    yield db
    app.dependency_overrides.clear()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "user"}

def test_list_users(mock_db):
    mock_user = User(id=1, name="John Doe", email="john@example.com", created_at=datetime(2024, 1, 1))
    mock_db.query.return_value.order_by.return_value.all.return_value = [mock_user]
    
    response = client.get("/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "John Doe"

def test_get_user_found(mock_db):
    mock_user = User(id=1, name="John Doe", email="john@example.com", created_at=datetime(2024, 1, 1))
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["name"] == "John Doe"

def test_get_user_not_found(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"
