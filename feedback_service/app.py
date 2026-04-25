from datetime import datetime

from fastapi import Depends, FastAPI
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Session

from common.database import Base, get_db


class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = {"schema": "aleksei_feedback_service"}

    id = Column(Integer, primary_key=True)
    entry_id = Column(
        Integer,
        ForeignKey("aleksei_competition_service.entries.id"),
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("aleksei_user_service.users.id"),
        nullable=False,
    )
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = {"schema": "aleksei_feedback_service"}

    id = Column(Integer, primary_key=True)
    entry_id = Column(
        Integer,
        ForeignKey("aleksei_competition_service.entries.id"),
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("aleksei_user_service.users.id"),
        nullable=False,
    )
    score = Column(Integer, nullable=False)


app = FastAPI(title="Feedback Service")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "feedback"}


@app.get("/feedback")
def list_feedback(
    entry_id: int | None = None,
    db: Session = Depends(get_db),
) -> list[dict]:
    q = db.query(Feedback)
    if entry_id is not None:
        q = q.filter(Feedback.entry_id == entry_id)
    rows = q.order_by(Feedback.id.asc()).all()

    def _ts(v: datetime | str) -> str:
        return v.isoformat() if isinstance(v, datetime) else str(v)

    return [
        {
            "id": r.id,
            "entry_id": r.entry_id,
            "user_id": r.user_id,
            "comment": r.comment,
            "created_at": _ts(r.created_at),
        }
        for r in rows
    ]


@app.get("/ratings")
def list_ratings(
    entry_id: int | None = None,
    db: Session = Depends(get_db),
) -> list[dict]:
    q = db.query(Rating)
    if entry_id is not None:
        q = q.filter(Rating.entry_id == entry_id)
    rows = q.order_by(Rating.id.asc()).all()
    return [
        {
            "id": r.id,
            "entry_id": r.entry_id,
            "user_id": r.user_id,
            "score": r.score,
        }
        for r in rows
    ]

