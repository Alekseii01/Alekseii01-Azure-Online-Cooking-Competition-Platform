from fastapi import Depends, FastAPI
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Session

from common.database import Base, get_db


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {"schema": "aleksei_recipe_service"}

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)


class Recipe(Base):
    __tablename__ = "recipes"
    __table_args__ = {"schema": "aleksei_recipe_service"}

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    author_id = Column(
        Integer,
        ForeignKey("aleksei_user_service.users.id"),
        nullable=False,
    )
    category_id = Column(
        Integer,
        ForeignKey("aleksei_recipe_service.categories.id"),
        nullable=False,
    )


class Ingredient(Base):
    __tablename__ = "ingredients"
    __table_args__ = {"schema": "aleksei_recipe_service"}

    id = Column(Integer, primary_key=True)
    recipe_id = Column(
        Integer,
        ForeignKey("aleksei_recipe_service.recipes.id"),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    quantity = Column(String(255), nullable=False)


app = FastAPI(title="Recipe Service")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "recipe"}


@app.get("/categories")
def list_categories(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(Category).order_by(Category.id.asc()).all()
    return [{"id": r.id, "name": r.name} for r in rows]


@app.get("/recipes")
def list_recipes(
    category_id: int | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
) -> list[dict]:
    q = db.query(Recipe)
    if category_id is not None:
        q = q.filter(Recipe.category_id == category_id)
    if search:
        q = q.filter(Recipe.title.ilike(f"%{search}%"))
    rows = q.order_by(Recipe.id.asc()).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "author_id": r.author_id,
            "category_id": r.category_id,
        }
        for r in rows
    ]


@app.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int, db: Session = Depends(get_db)) -> dict:
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Recipe not found")

    ingredients = (
        db.query(Ingredient)
        .filter(Ingredient.recipe_id == recipe_id)
        .order_by(Ingredient.id.asc())
        .all()
    )

    return {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "author_id": recipe.author_id,
        "category_id": recipe.category_id,
        "ingredients": [
            {"id": i.id, "name": i.name, "quantity": i.quantity}
            for i in ingredients
        ],
    }


@app.get("/ingredients")
def list_ingredients(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(Ingredient).order_by(Ingredient.id.asc()).all()
    return [
        {
            "id": r.id,
            "recipe_id": r.recipe_id,
            "name": r.name,
            "quantity": r.quantity,
        }
        for r in rows
    ]

