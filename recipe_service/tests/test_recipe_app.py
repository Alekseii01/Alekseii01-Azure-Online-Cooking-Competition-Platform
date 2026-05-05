import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from recipe_service.app import app, Recipe, Category, Ingredient, get_db

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
    assert response.json() == {"status": "ok", "service": "recipe"}

def test_list_recipes_filter(mock_db):
    mock_recipe = Recipe(id=1, title="Pasta", description="Yummy", author_id=1, category_id=1)
    # Mocking the filter chain
    mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_recipe]
    
    response = client.get("/recipes?category_id=1&search=Pasta")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Pasta"

def test_get_recipe_with_ingredients(mock_db):
    mock_recipe = Recipe(id=1, title="Pasta", description="Yummy", author_id=1, category_id=1)
    mock_ingredient = Ingredient(id=1, recipe_id=1, name="Flour", quantity="1kg")
    
    mock_db.query.return_value.filter.return_value.first.return_value = mock_recipe
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_ingredient]
    
    response = client.get("/recipes/1")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Pasta"
    assert len(data["ingredients"]) == 1
    assert data["ingredients"][0]["name"] == "Flour"
