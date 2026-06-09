from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr | None = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None


class SubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    char_code: str


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    subscriptions: list[SubscriptionOut] = []


class CurrencyRate(BaseModel):
    num_code: str
    char_code: str
    nominal: int
    name: str
    value: float
    unit_value: float
    date: str


class UserSubscribedRate(BaseModel):
    subscription: SubscriptionOut
    rate: CurrencyRate | None = None
