import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime
from feedback_service.app import app, Feedback, Rating, get_db

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
    assert response.json() == {"status": "ok", "service": "feedback"}

def test_list_feedback_filter(mock_db):
    mock_fb = Feedback(id=1, entry_id=1, user_id=1, comment="Good!", created_at=datetime(2024, 1, 1))
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_fb]
    
    response = client.get("/feedback?entry_id=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["comment"] == "Good!"

def test_list_ratings_filter(mock_db):
    mock_rating = Rating(id=1, entry_id=1, user_id=1, score=5)
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_rating]
    
    response = client.get("/ratings?entry_id=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["score"] == 5
