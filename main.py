from typing import Optional

from fastapi import FastAPI

from models import ModelName

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]
    return fake_items_db[skip : skip + limit]


@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


@app.get("/items/optional/{item_id}")
def read_item_optional(item_id: str, optional_str: Optional[str] = None):
    if optional_str:
        return {"item_id": item_id, "optional_str": optional_str}
    return {"item_id": item_id}


@app.get("/items/optional/bool/{item_id}")
def read_item_optional_and_bool(
    item_id: str, optional_str: Optional[str] = None, include_description: bool = False
):
    item = {"item_id": item_id}
    if optional_str:
        item.update({"optional_str": optional_str})
    if include_description:
        item.update({"description": "This item includes a description"})
    return item


@app.get("/users/me")
def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
def read_user(user_id: str):
    return {"user_id": user_id}


@app.get("/users/{user_id}/items/{item_id}")
def read_user_item(
    user_id: int,
    item_id: str,
    optional_str: Optional[str] = None,
    include_description: bool = False,
):
    item = {"item_id": item_id, "owner_id": user_id}
    if optional_str:
        item.update({"optional_str": optional_str})
    if include_description:
        item.update({"description": "This item includes a description"})
    return item


@app.get("/models/{model_name}")
def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/files/{file_path:path}")
def read_file(file_path: str):
    """
    >>> read_file("/home/johndoe/myfile.txt")
    {'file_path': '/home/johndoe/myfile.txt'}
    """
    return {"file_path": file_path}
