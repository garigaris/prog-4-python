from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)

    subscriptions: Mapped[list["CurrencySubscription"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class CurrencySubscription(Base):
    __tablename__ = "currency_subscriptions"
    __table_args__ = (
        UniqueConstraint("user_id", "char_code", name="uq_user_currency"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    char_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    user: Mapped[User] = relationship(back_populates="subscriptions")
