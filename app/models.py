from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


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
