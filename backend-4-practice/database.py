from pathlib import Path

from sqlalchemy import URL, create_engine, event, select
from sqlalchemy.orm import Session

from models import Base, Category, Master


DATABASE_PATH = Path(__file__).resolve().parent / "salon.db"
engine = create_engine(URL.create("sqlite", database=str(DATABASE_PATH)))


@event.listens_for(engine, "connect")
def enable_foreign_keys(connection, connection_record):
    connection.execute("PRAGMA foreign_keys = ON")


def init_db() -> None:
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        if session.scalar(select(Master.id).limit(1)) is None:
            session.add_all([
                Master(name="Анна", specialization="Парикмахер"),
                Master(name="Мария", specialization="Визажист"),
            ])
        if session.scalar(select(Category.id).limit(1)) is None:
            session.add_all([
                Category(id=1, name="Стрижки и укладки"),
                Category(id=2, name="Борода и усы"),
                Category(id=3, name="Уход за волосами"),
            ])
        session.commit()
