import os
from collections.abc import Generator
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

load_dotenv()

_raw = (
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={os.getenv('DB_SERVER', '')};"
    f"DATABASE={os.getenv('DB_DATABASE', '')};"
    f"UID={os.getenv('DB_USERNAME', '')};"
    f"PWD={os.getenv('DB_PASSWORD', '')};"
    f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
)

engine = create_engine(
    "mssql+pyodbc:///?odbc_connect=" + quote_plus(_raw),
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
