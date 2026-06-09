from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Path, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.cbr_client import CBRServiceError, fetch_currency_rate, fetch_currency_rates
from app.database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Currency Subscription API",
    description="FastAPI + SQLAlchemy + SQLite приложение для подписки пользователей на курсы валют ЦБ РФ.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "message": "Currency Subscription API работает"}


@app.post("/users", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_user(db, user)
    except crud.DuplicateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@app.get("/users", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return crud.get_users(db)


@app.get("/users/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return db_user


@app.put("/users/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    try:
        db_user = crud.update_user(db, user_id, user)
    except crud.DuplicateError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return db_user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return None


@app.post(
    "/users/{user_id}/subscriptions/{char_code}",
    response_model=schemas.SubscriptionOut,
    status_code=status.HTTP_201_CREATED,
)
def subscribe_to_currency(
    user_id: int,
    char_code: str = Path(min_length=3, max_length=10, examples=["USD"]),
    db: Session = Depends(get_db),
):
    # Проверяем, что такая валюта реально есть в свежей выгрузке ЦБ.
    try:
        rate = fetch_currency_rate(char_code)
    except CBRServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    if rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Валюта не найдена в данных ЦБ РФ")

    subscription = crud.subscribe(db, user_id, char_code)
    if subscription is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return subscription


@app.delete("/users/{user_id}/subscriptions/{char_code}", status_code=status.HTTP_204_NO_CONTENT)
def unsubscribe_from_currency(
    user_id: int,
    char_code: str = Path(min_length=3, max_length=10, examples=["USD"]),
    db: Session = Depends(get_db),
):
    result = crud.unsubscribe(db, user_id, char_code)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    if result is False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Подписка не найдена")
    return None


@app.get("/users/{user_id}/subscriptions", response_model=list[schemas.SubscriptionOut])
def list_user_subscriptions(user_id: int, db: Session = Depends(get_db)):
    subscriptions = crud.get_user_subscriptions(db, user_id)
    if subscriptions is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return subscriptions


@app.get("/rates", response_model=list[schemas.CurrencyRate])
def get_rates():
    try:
        rates = fetch_currency_rates()
    except CBRServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return list(rates.values())


@app.get("/rates/{char_code}", response_model=schemas.CurrencyRate)
def get_rate(char_code: str = Path(min_length=3, max_length=10, examples=["USD"])):
    try:
        rate = fetch_currency_rate(char_code)
    except CBRServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    if rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Валюта не найдена в данных ЦБ РФ")
    return rate


@app.get("/users/{user_id}/rates", response_model=list[schemas.UserSubscribedRate])
def get_user_subscribed_rates(user_id: int, db: Session = Depends(get_db)):
    subscriptions = crud.get_user_subscriptions(db, user_id)
    if subscriptions is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    try:
        rates = fetch_currency_rates()
    except CBRServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    return [
        schemas.UserSubscribedRate(subscription=subscription, rate=rates.get(subscription.char_code))
        for subscription in subscriptions
    ]
