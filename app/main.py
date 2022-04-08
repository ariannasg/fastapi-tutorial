from datetime import datetime, time, timedelta
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import Body, Cookie, FastAPI, Header, Path, Query

from models import (
    Image,
    Item,
    ItemWithFields,
    ItemWithNestedModel,
    ModelName,
    Offer,
    User,
)

tutorial_app = FastAPI()


@tutorial_app.get("/")
def root():
    return {"message": "Hello World"}


@tutorial_app.post("/items/")
def create_item(item: Item):
    return item


@tutorial_app.post("/items/derived_attrs")
def create_item_derived_attrs(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@tutorial_app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]
    return fake_items_db[skip : skip + limit]


@tutorial_app.get("/items_params/required_max_length")
def read_items_params_required_max_length(required_str: str = Query(..., max_length=3)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    results.update({"required_str": required_str})
    return results


@tutorial_app.get("/items_params/optional_max_length")
def read_items_params_optional_max_length(
    optional_str: Optional[str] = Query(None, max_length=3)
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if optional_str:
        results.update({"optional_str": optional_str})
    return results


@tutorial_app.get("/items_params_optional_regex")
def read_items_params_optional_regex(
    optional_str: Optional[str] = Query(
        None, min_length=3, max_length=50, regex="^fixedoptional_str$"
    )
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if optional_str:
        results.update({"optional_str": optional_str})
    return results


@tutorial_app.get("/items_params_regex_default")
def read_items_params_regex_default(
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


@tutorial_app.get("/items_params/optional_list")
def read_items_params_optional_list(optional_str: Optional[List[str]] = Query(None)):
    optional_str = {"optional_str": optional_str}
    return optional_str


@tutorial_app.get("/items_params/default_list_typing")
def read_items_params_default_list_typing(
    required_str_str: List[str] = Query(["foo", "bar"])
):
    required_str_str_items = {"required_str_str": required_str_str}
    return required_str_str_items


@tutorial_app.get("/items_params/required_str_list_native")
def read_items_params_required_str_list_native(
    required_str_str: list = Query([]),
):
    optional_str_items = {"required_str_str": required_str_str}
    return optional_str_items


@tutorial_app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


@tutorial_app.get("/items/optional/{item_id}")
def read_item_optional(item_id: str, optional_str: Optional[str] = None):
    if optional_str:
        return {"item_id": item_id, "optional_str": optional_str}
    return {"item_id": item_id}


@tutorial_app.get("/items/optional/bool/{item_id}")
def read_item_optional_and_bool(
    item_id: str, optional_str: Optional[str] = None, include_description: bool = False
):
    item = {"item_id": item_id}
    if optional_str:
        item.update({"optional_str": optional_str})
    if include_description:
        item.update({"description": "This item includes a description"})
    return item


@tutorial_app.get("/items_params_metadata_and_validation")
def read_items_params_metadata_and_validation(
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


@tutorial_app.get("/items_params_alias")
def read_items_params_alias(required_str: str = Query(..., alias="item-query")):
    results = {
        "items": [
            {"item_id": "Foo"},
            {"item_id": "Bar"},
            {"required_str": required_str},
        ]
    }
    return results


@tutorial_app.get("/items_params_deprecated")
def read_items_params_deprecated(required_str: str = Query(..., deprecated=True)):
    results = {
        "items": [
            {"item_id": "Foo"},
            {"item_id": "Bar"},
            {"required_str": required_str},
        ]
    }
    return results


@tutorial_app.get("/items_params_hidden_in_openapi")
def read_items_params_hidden_in_openapi(
    hidden_query: Optional[str] = Query(None, include_in_schema=False)
):
    if hidden_query:
        return {"hidden_query": hidden_query}
    return {"hidden_query": "Not found"}


@tutorial_app.get("/items_path_metadata/{item_id}")
def read_items_path_metadata(
    item_id: int = Path(..., description="The ID of the item to get"),
    optional_str: Optional[str] = Query(None, alias="item-query"),
):
    results = {"item_id": item_id}
    if optional_str:
        results.update({"optional_str": optional_str})
    return results


@tutorial_app.get("/items_path_order/{item_id}")
def read_items_path_order(
    *,
    item_id: int = Path(..., description="The ID of the item to get"),
    required_str: str,
):
    results = {"item_id": item_id, "required_str": required_str}
    return results


@tutorial_app.get("/items_path_validation/{item_id}")
def items_path_validation(
    *,
    item_id: int = Path(..., description="The ID of the item to get", ge=1, lt=10),
    required_str: str,
):
    results = {"item_id": item_id, "required_str": required_str}
    return results


@tutorial_app.get("/items_with_cookies/")
def read_items_with_cookies(ads_id: Optional[str] = Cookie(None)):
    return {"ads_id": ads_id}


@tutorial_app.get("/items_with_headers/")
def read_items_with_headers(
    user_agent: Optional[str] = Header(None, include_in_schema=False)
):
    """
    By default, Header will convert the parameter names characters from underscore (_)
    to hyphen (-) to extract and document the headers.
    """
    return {"User-Agent": user_agent}


@tutorial_app.get("/items_headers_without_conversion/")
def read_items_headers_without_conversion(
    strange_header: Optional[str] = Header(None, convert_underscores=False)
):
    return {"strange_header": strange_header}


@tutorial_app.get("/items_with_duplicated_headers/")
def read_items_with_duplicated_headers(x_token: Optional[List[str]] = Header(None)):
    return {"X-Token values": x_token}


@tutorial_app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}


@tutorial_app.put("/items_multiple_models/{item_id}")
def update_item_multiple_models(item_id: int, item: Item, user: User):
    results = {"item_id": item_id, "item": item, "user": user}
    return results


@tutorial_app.put("/items_extra_body_param/{item_id}")
def update_item_extra_body_param(
    item_id: int,
    item: Item,
    user: User,
    extra_required_int_param: int = Body(
        ..., description="Extra required body parameter"
    ),
):
    results = {
        "item_id": item_id,
        "item": item,
        "user": user,
        "extra_required_int_param": extra_required_int_param,
    }
    return results


@tutorial_app.put("/items_embedded/{item_id}")
def update_item_embedded(item_id: int, embedded_item: Item = Body(..., embed=True)):
    results = {"item_id": item_id, "embedded_item": embedded_item}
    return results


@tutorial_app.put("/items_with_fields/{item_id}")
def update_item_with_fields(
    item_id: int, item_with_fields: ItemWithFields = Body(..., embed=True)
):
    results = {"item_id": item_id, "item": item_with_fields}
    return results


@tutorial_app.put("/items_with_nested_model/{item_id}")
def update_item_with_nested_model(
    item_id: int, item_with_nested_model: ItemWithNestedModel
):
    results = {"item_id": item_id, "item_with_nested_model": item_with_nested_model}
    return results


@tutorial_app.put("/items_with_example/{item_id}")
def update_item_with_example(
    item_id: int,
    item: Item = Body(
        ...,
        example={
            "name": "Foo",
            "description": "A very nice Item",
            "price": 35.4,
            "tax": 3.2,
        },
    ),
):
    results = {"item_id": item_id, "item": item}
    return results


@tutorial_app.put("/items_with_multiple_examples/{item_id}")
def update_item_with_multiple_examples(
    *,
    item_id: int,
    item: Item = Body(
        ...,
        examples={
            "normal": {
                "summary": "A normal example",
                "description": "A **normal** item works correctly.",
                "value": {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                },
            },
            "converted": {
                "summary": "An example with converted data",
                "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                "value": {
                    "name": "Bar",
                    "price": "35.4",
                },
            },
            "invalid": {
                "summary": "Invalid data is rejected with an error",
                "value": {
                    "name": "Baz",
                    "price": "thirty five point four",
                },
            },
        },
    ),
):
    results = {"item_id": item_id, "item": item}
    return results


@tutorial_app.put("/items_extra_datatypes/{item_id}")
def read_items_extra_datatypes(
    item_id: UUID,
    start_datetime: Optional[datetime] = Body(None),
    end_datetime: Optional[datetime] = Body(None),
    repeat_at: Optional[time] = Body(None),
    process_after: Optional[timedelta] = Body(None),
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": repeat_at,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration,
    }


@tutorial_app.get("/users/me")
def read_user_me():
    return {"user_id": "the current user"}


@tutorial_app.get("/users/{user_id}")
def read_user(user_id: str):
    return {"user_id": user_id}


@tutorial_app.get("/users/{user_id}/items/{item_id}")
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


@tutorial_app.get("/models/{model_name}")
def get_model(model_name: ModelName):
    if model_name == ModelName.ALEXNET:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@tutorial_app.get("/files/{file_path:path}")
def read_file(file_path: str):
    """
    >>> read_file("/home/johndoe/myfile.txt")
    {'file_path': '/home/johndoe/myfile.txt'}
    """
    return {"file_path": file_path}


@tutorial_app.post("/offers/")
def create_offer(offer: Offer):
    return offer


@tutorial_app.post("/images/multiple/")
def create_multiple_images(images: List[Image]):
    return images


@tutorial_app.post("/index-weights/")
def create_index_weights(weights: Dict[str, float]):
    return weights
