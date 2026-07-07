from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, String, Integer

class Base(DeclarativeBase):
    pass

class Character(Base):
    __tablename__ = "characters"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String(50))
    char_class: Mapped[int] = mapped_column(Integer)
    difficulty: Mapped[int] = mapped_column(Integer)

    hp: Mapped[int] = mapped_column(Integer, default=100)
    max_hp: Mapped[int] = mapped_column(Integer, default=100)
    level: Mapped[int] = mapped_column(Integer, default=1)
    xp: Mapped[int] = mapped_column(Integer, default=0)
