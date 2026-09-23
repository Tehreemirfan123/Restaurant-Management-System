from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# .env is loaded once in core.config; import the resolved URL from there so
# there is a single source of truth and no duplicate load_dotenv calls.
from core.config import DATABASE_URL


engine = create_engine(
    DATABASE_URL,
    # Recycle connections so a restarted/timed-out DB doesn't hand back a
    # dead connection, and verify liveness before use.
    pool_pre_ping=True,
    pool_recycle=1800,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db: Session = SessionLocal()

    try:
        yield db
    except Exception:
        # Roll back a half-finished unit of work before the connection is
        # returned to the pool, so a failed request never leaks a dirty session.
        db.rollback()
        raise
    finally:
        db.close()