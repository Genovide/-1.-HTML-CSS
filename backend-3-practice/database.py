from pathlib import Path

from sqlalchemy import URL, create_engine, select
from sqlalchemy.orm import Session

from models import Base, Master


DATABASE_PATH = Path(__file__).resolve().parent / "salon.db"
engine = create_engine(URL.create("sqlite", database=str(DATABASE_PATH)))


def init_db() -> None:
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        if session.scalar(select(Master.id).limit(1)) is None:
            session.add_all([
                Master(name="Анна", specialization="Парикмахер"),
                Master(name="Мария", specialization="Визажист"),
            ])
            session.commit()
