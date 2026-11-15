from sqlalchemy import CheckConstraint, Float, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Master(Base):
    __tablename__ = "masters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    specialization: Mapped[str] = mapped_column(String(100), nullable=False)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class Service(Base):
    __tablename__ = "services"
    __table_args__ = (
        CheckConstraint("length(title) BETWEEN 1 AND 100"),
        CheckConstraint("length(desc) BETWEEN 1 AND 100"),
        CheckConstraint("duration BETWEEN 30 AND 180"),
        CheckConstraint("price > 0"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    desc: Mapped[str] = mapped_column(String(100), nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
