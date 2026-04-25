from datetime import datetime

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Session

from common.database import Base, get_db
from common.message_bus import publish_message

load_dotenv()


class Competition(Base):
    __tablename__ = "competitions"
    __table_args__ = {"schema": "aleksei_competition_service"}

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False)


class Entry(Base):
    __tablename__ = "entries"
    __table_args__ = {"schema": "aleksei_competition_service"}

    id = Column(Integer, primary_key=True)
    competition_id = Column(
        Integer,
        ForeignKey("aleksei_competition_service.competitions.id"),
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("aleksei_user_service.users.id"),
        nullable=False,
    )
    recipe_id = Column(
        Integer,
        ForeignKey("aleksei_recipe_service.recipes.id"),
        nullable=False,
    )
    status = Column(String(50), nullable=False)


app = FastAPI(title="Competition Service")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "competition"}


@app.get("/competitions")
def list_competitions(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(Competition).order_by(Competition.id.asc()).all()

    def _ts(v: datetime | str) -> str:
        return v.isoformat() if isinstance(v, datetime) else str(v)

    return [
        {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "start_date": _ts(r.start_date),
            "end_date": _ts(r.end_date),
            "status": r.status,
        }
        for r in rows
    ]


@app.get("/competitions/{competition_id}")
def get_competition(competition_id: int, db: Session = Depends(get_db)) -> dict:
    comp = db.query(Competition).filter(Competition.id == competition_id).first()
    if not comp:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Competition not found")

    def _ts(v: datetime | str) -> str:
        return v.isoformat() if isinstance(v, datetime) else str(v)

    return {
        "id": comp.id,
        "title": comp.title,
        "description": comp.description,
        "start_date": _ts(comp.start_date),
        "end_date": _ts(comp.end_date),
        "status": comp.status,
    }


@app.get("/entries")
def list_entries(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(Entry).order_by(Entry.id.asc()).all()
    return [
        {
            "id": r.id,
            "competition_id": r.competition_id,
            "user_id": r.user_id,
            "recipe_id": r.recipe_id,
            "status": r.status,
        }
        for r in rows
    ]


@app.get("/competitions/{competition_id}/entries")
def list_entries_by_competition(
    competition_id: int, db: Session = Depends(get_db)
) -> list[dict]:
    rows = (
        db.query(Entry)
        .filter(Entry.competition_id == competition_id)
        .order_by(Entry.id.asc())
        .all()
    )
    result = [
        {
            "id": r.id,
            "competition_id": r.competition_id,
            "user_id": r.user_id,
            "recipe_id": r.recipe_id,
            "status": r.status,
        }
        for r in rows
    ]
    publish_message({
        "event": "entries_viewed",
        "competition_id": competition_id,
        "entry_count": len(result),
    })
    return result

