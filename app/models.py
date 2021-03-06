from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from database import Base


class ModelName(str, Enum):
    ALEXNET = "alexnet"
    RESNET = "resnet"
    LENET = "lenet"


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


class User(BaseModel):
    username: str
    full_name: Optional[str] = None


class ItemWithFields(BaseModel):
    name: str
    description: Optional[str] = Field(
        None, title="The description of the item", max_length=300
    )
    price: float = Field(
        ..., gt=0, description="The price must be greater than zero", example=0.4
    )
    tax: Optional[float] = None


class Image(BaseModel):
    url: HttpUrl
    name: str


class ItemWithNestedModel(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    image: Optional[Image] = None


class Offer(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    items: List[ItemWithNestedModel]


class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print(f"User saved with hashed_password pwd: {hashed_password} ...not really")
    return user_in_db


class BaseItem(BaseModel):
    description: str
    type: str


class CarItem(BaseItem):
    type = "car"


class PlaneItem(BaseItem):
    type = "plane"
    size: int


class Tags(Enum):
    ENDPOINT_WITH_TAG_1 = "Tag 1"
    ENDPOINT_WITH_TAG_2 = "Tag 2"


class Pet(BaseModel):
    type: str
    name: str


class ItemWithDatetime(BaseModel):
    title: str
    timestamp: datetime
    description: Optional[str] = None


class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}


class AuthUser(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class AuthUserInDB(AuthUser):
    hashed_password: str


def fake_hash_password(password: str):
    return "fakehashed" + password


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return AuthUserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


class SQLUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)


def get_sql_user(db: Session, user_id: int):
    return db.query(SQLUser).filter(SQLUser.id == user_id).first()


def get_sql_user_by_email(db: Session, email: str):
    return db.query(SQLUser).filter(SQLUser.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(SQLUser).offset(skip).limit(limit).all()
