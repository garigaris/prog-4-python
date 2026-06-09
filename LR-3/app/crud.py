from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app import models, schemas


class DuplicateError(Exception):
    pass


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateError("Пользователь с таким email уже существует") from exc
    db.refresh(db_user)
    return db_user


def get_users(db: Session) -> list[models.User]:
    stmt = select(models.User).options(selectinload(models.User.subscriptions)).order_by(models.User.id)
    return list(db.scalars(stmt).all())


def get_user(db: Session, user_id: int) -> models.User | None:
    stmt = (
        select(models.User)
        .where(models.User.id == user_id)
        .options(selectinload(models.User.subscriptions))
    )
    return db.scalar(stmt)


def update_user(db: Session, user_id: int, data: schemas.UserUpdate) -> models.User | None:
    db_user = get_user(db, user_id)
    if db_user is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateError("Пользователь с таким email уже существует") from exc
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    db_user = get_user(db, user_id)
    if db_user is None:
        return False

    db.delete(db_user)
    db.commit()
    return True


def get_subscription(db: Session, user_id: int, char_code: str) -> models.CurrencySubscription | None:
    stmt = select(models.CurrencySubscription).where(
        models.CurrencySubscription.user_id == user_id,
        models.CurrencySubscription.char_code == char_code.upper(),
    )
    return db.scalar(stmt)


def subscribe(db: Session, user_id: int, char_code: str) -> models.CurrencySubscription | None:
    db_user = get_user(db, user_id)
    if db_user is None:
        return None

    normalized_code = char_code.upper()
    existing = get_subscription(db, user_id, normalized_code)
    if existing is not None:
        return existing

    subscription = models.CurrencySubscription(user_id=user_id, char_code=normalized_code)
    db.add(subscription)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateError("Подписка на эту валюту уже существует") from exc
    db.refresh(subscription)
    return subscription


def unsubscribe(db: Session, user_id: int, char_code: str) -> bool | None:
    if get_user(db, user_id) is None:
        return None

    subscription = get_subscription(db, user_id, char_code)
    if subscription is None:
        return False

    db.delete(subscription)
    db.commit()
    return True


def get_user_subscriptions(db: Session, user_id: int) -> list[models.CurrencySubscription] | None:
    if get_user(db, user_id) is None:
        return None

    stmt = (
        select(models.CurrencySubscription)
        .where(models.CurrencySubscription.user_id == user_id)
        .order_by(models.CurrencySubscription.char_code)
    )
    return list(db.scalars(stmt).all())
