import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from datetime import datetime
from competition_service.app import app, Competition, Entry, get_db

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
    assert response.json() == {"status": "ok", "service": "competition"}

def test_list_competitions(mock_db):
    mock_comp = Competition(id=1, title="Cooking Challenge", description="Desc", 
                            start_date=datetime(2024, 1, 1), end_date=datetime(2024, 1, 2), status="active")
    mock_db.query.return_value.order_by.return_value.all.return_value = [mock_comp]
    
    response = client.get("/competitions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Cooking Challenge"

def test_list_entries_by_competition(mock_db):
    mock_entry = Entry(id=1, competition_id=1, user_id=1, recipe_id=1, status="submitted")
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_entry]
    
    with patch("competition_service.app.publish_message") as mock_publish:
        response = client.get("/competitions/1/entries")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        mock_publish.assert_called_once()
