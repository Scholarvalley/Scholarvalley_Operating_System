from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings


settings = get_settings()

engine = create_engine(settings.database_url, echo=False, future=True)


def init_db() -> None:
    # For early development only; in production use Alembic migrations.
    SQLModel.metadata.create_all(bind=engine)


def get_session():
    with Session(engine) as session:
        yield session

