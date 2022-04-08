from typing import List, Optional

from fastapi import FastAPI, Query

from models import Item, ModelName

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/items/")
def create_item(item: Item):
    return item


@app.post("/items/derived_attrs")
def create_item_derived_attrs(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]
    return fake_items_db[skip : skip + limit]


@app.get("/items/required_max_length")
def read_items_required_max_length(required_str: str = Query(..., max_length=3)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    results.update({"required_str": required_str})
    return results


@app.get("/items/optional_max_length")
def read_items_optional_max_length(
    optional_str: Optional[str] = Query(None, max_length=3)
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if optional_str:
        results.update({"optional_str": optional_str})
    return results


@app.get("/items/regex")
def read_items_optional_regex(
    optional_str: Optional[str] = Query(
        None, min_length=3, max_length=50, regex="^fixedoptional_str$"
    )
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if optional_str:
        results.update({"optional_str": optional_str})
    return results


@app.get("/items/regex/default")
def read_items_optional_regex_default(
    optional_str: Optional[str] = Query(
        "fixedoptional_str",
        min_length=3,
        max_length=50,
        regex="^fixedoptional_str$",
    )
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if optional_str:
        results.update({"optional_str": optional_str})
    return results


@app.get("/items/optional_list")
def read_items_optional_list(optional_str: Optional[List[str]] = Query(None)):
    optional_str = {"optional_str": optional_str}
    return optional_str


@app.get("/items/default_list_typing")
def read_items_default_list_typing(required_str_str: List[str] = Query(["foo", "bar"])):
    required_str_str_items = {"required_str_str": required_str_str}
    return required_str_str_items


@app.get("/items/required_str_list_native")
def read_items_required_str_list_native(
    required_str_str: list = Query([]),
):
    optional_str_items = {"required_str_str": required_str_str}
    return optional_str_items


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


@app.get("/items_metadata")
def read_items_metadata_and_validation(
    required_str: str = Query(
        ...,
        title="Query string",
        description="Query string for the items to search in the database that have a good match",
    )
):
    results = {
        "items": [
            {"item_id": "Foo"},
            {"item_id": "Bar"},
            {"required_str": required_str},
        ]
    }
    return results


@app.get("/items_alias")
def read_items_alias(required_str: str = Query(..., alias="item-query")):
    results = {
        "items": [
            {"item_id": "Foo"},
            {"item_id": "Bar"},
            {"required_str": required_str},
        ]
    }
    return results


@app.get("/items_deprecated")
def read_items_deprecated(required_str: str = Query(..., deprecated=True)):
    results = {
        "items": [
            {"item_id": "Foo"},
            {"item_id": "Bar"},
            {"required_str": required_str},
        ]
    }
    return results


@app.get("/items_hidden_in_openapi")
def read_items_hidden_in_openapi(
    hidden_query: Optional[str] = Query(None, include_in_schema=False)
):
    if hidden_query:
        return {"hidden_query": hidden_query}
    else:
        return {"hidden_query": "Not found"}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}


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
