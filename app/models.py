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


class UserIn(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None


class UserOut(BaseModel):
    username: str
    full_name: Optional[str] = None
