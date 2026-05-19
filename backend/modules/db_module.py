from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Import the settings from your new config module
from ..config import settings

DATABASE_URL = (
    f"postgresql+psycopg://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def select_query(db: Session, query_text: str, params: dict = None) -> list[dict]:
    """
    Execute a dynamic SELECT query and return results as a list of dicts.
    
    :param db: SQLAlchemy session
    :param query_text: Raw SQL SELECT string, e.g. "SELECT * FROM users WHERE id = :id"
    :param params: Optional dict of bind parameters, e.g. {"id": 1}
    """
    try:
        result = db.execute(text(query_text), params or {})
        rows = result.fetchall()
        columns = result.keys()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        raise RuntimeError(f"Query failed: {str(e)}")
