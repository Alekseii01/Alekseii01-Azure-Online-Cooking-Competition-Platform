from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True, scope="session")
def patch_db_engine():
    with patch("common.database.create_engine", return_value=MagicMock()):
        yield


@pytest.fixture()
def client():
    from app import app
    return TestClient(app)


class TestHealth:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "recipe"


class TestCategories:
    def test_list_categories_empty(self, client):
        from app import get_db

        mock_db = MagicMock()
        mock_db.query.return_value.order_by.return_value.all.return_value = []

        from app import app
        app.dependency_overrides[get_db] = lambda: mock_db
        response = client.get("/categories")
        app.dependency_overrides.clear()

        assert response.status_code == 200
        assert response.json() == []

    def test_list_categories_returns_data(self, client):
        from app import Category, get_db

        mock_cat = MagicMock(spec=Category)
        mock_cat.id = 1
        mock_cat.name = "Desserts"

        mock_db = MagicMock()
        mock_db.query.return_value.order_by.return_value.all.return_value = [mock_cat]

        from app import app
        app.dependency_overrides[get_db] = lambda: mock_db
        response = client.get("/categories")
        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["name"] == "Desserts"


class TestRecipes:
    def test_list_recipes_empty(self, client):
        from app import get_db

        mock_db = MagicMock()
        mock_db.query.return_value.order_by.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        from app import app
        app.dependency_overrides[get_db] = lambda: mock_db
        response = client.get("/recipes")
        app.dependency_overrides.clear()

        assert response.status_code == 200
        assert response.json() == []

    def test_get_recipe_not_found(self, client):
        from app import get_db

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        from app import app
        app.dependency_overrides[get_db] = lambda: mock_db
        response = client.get("/recipes/999")
        app.dependency_overrides.clear()

        assert response.status_code == 404
        assert response.json()["detail"] == "Recipe not found"

    def test_get_recipe_found(self, client):
        from app import Ingredient, Recipe, get_db

        mock_recipe = MagicMock(spec=Recipe)
        mock_recipe.id = 5
        mock_recipe.title = "Chocolate Cake"
        mock_recipe.description = "Delicious cake"
        mock_recipe.author_id = 1
        mock_recipe.category_id = 2

        mock_ingredient = MagicMock(spec=Ingredient)
        mock_ingredient.id = 10
        mock_ingredient.name = "Flour"
        mock_ingredient.quantity = "200g"

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_recipe
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_ingredient]

        from app import app
        app.dependency_overrides[get_db] = lambda: mock_db
        response = client.get("/recipes/5")
        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 5
        assert data["title"] == "Chocolate Cake"
        assert len(data["ingredients"]) == 1
        assert data["ingredients"][0]["name"] == "Flour"
