from datetime import datetime

from fastapi import Depends, FastAPI
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Session

from common.database import Base, get_db


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "aleksei_user_service"}

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)


app = FastAPI(title="User Service")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "user"}


@app.get("/users")
def list_users(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(User).order_by(User.id.asc()).all()

    def _ts(v: datetime | str) -> str:
        return v.isoformat() if isinstance(v, datetime) else str(v)

    return [
        {
            "id": r.id,
            "name": r.name,
            "email": r.email,
            "created_at": _ts(r.created_at),
        }
        for r in rows
    ]


@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")

    def _ts(v: datetime | str) -> str:
        return v.isoformat() if isinstance(v, datetime) else str(v)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "created_at": _ts(user.created_at),
    }
