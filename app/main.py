import time as t
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Union
from uuid import UUID

from fastapi import (
    Body,
    Cookie,
    Depends,
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Request,
    status,
    UploadFile,
)
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from exceptions import UnicornException
from models import (
    AuthUser,
    AuthUserInDB,
    CarItem,
    CommonQueryParams,
    fake_decode_token,
    fake_hash_password,
    fake_save_user,
    fake_users_db,
    Image,
    Item,
    ItemWithDatetime,
    ItemWithFields,
    ItemWithNestedModel,
    ModelName,
    Offer,
    Pet,
    PlaneItem,
    Tags,
    User,
    UserIn,
    UserOut,
)

tutorial_app = FastAPI()


@tutorial_app.get("/")
def root():
    content = """
    <body>
    <form action="/files/" enctype="multipart/form-data" method="post">
    <input name="files" type="file" multiple>
    <input type="submit">
    </form>
    <form action="/uploadfiles/" enctype="multipart/form-data" method="post">
    <input name="files" type="file" multiple>
    <input type="submit">
    </form>
    </body>
    """
    return HTMLResponse(content=content)


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


@tutorial_app.post("/items_status_code/", status_code=status.HTTP_201_CREATED)
def create_item_status_code(name: str):
    return {"name": name}


@tutorial_app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]
    return fake_items_db[skip : skip + limit]


@tutorial_app.get("/items_with_depends/")
def read_items_with_depends(commons: CommonQueryParams = Depends()):
    fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    return response


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


@tutorial_app.get(
    "/items_response_model_exclude_unset/{item_id}",
    response_model=Item,
    response_model_exclude_unset=True,
)
def read_items_response_model_exclude_unset(item_id: str):
    items = {
        "foo": {"name": "Foo", "price": 50.2},
        "bar": {
            "name": "Bar",
            "description": "The bartenders",
            "price": 3.2,
            "tax": 20.2,
        },
        "baz": {"name": "Baz", "description": None, "price": 4.2, "tax": 10.5},
    }
    return items[item_id]


@tutorial_app.get(
    "/items/{item_id}/name",
    response_model=Item,
    response_model_include={"name"},
)
def read_item_name(item_id: str):
    items = {
        "foo": {"name": "Foo", "price": 50.2},
        "bar": {
            "name": "Bar",
            "description": "The bartenders",
            "price": 3.2,
            "tax": 20.2,
        },
        "baz": {"name": "Baz", "description": None, "price": 4.2, "tax": 10.5},
    }
    return items[item_id]


@tutorial_app.get(
    "/items/{item_id}/public", response_model=Item, response_model_exclude={"tax"}
)
def read_item_public_data(item_id: str):
    items = {
        "foo": {"name": "Foo", "price": 50.2},
        "bar": {
            "name": "Bar",
            "description": "The bartenders",
            "price": 3.2,
            "tax": 20.2,
        },
        "baz": {"name": "Baz", "description": None, "price": 4.2, "tax": 10.5},
    }
    return items[item_id]


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


@tutorial_app.get(
    "/items_planet_or_car/{item_id}", response_model=Union[PlaneItem, CarItem]
)
def read_item_planet_or_car(item_id: str):
    items = {
        "item1": {"description": "All my friends drive a low rider", "type": "car"},
        "item2": {
            "description": "Music is my aeroplane, it's my aeroplane",
            "type": "plane",
            "size": 5,
        },
    }
    return items[item_id]


@tutorial_app.get("/items_handling_error/{item_id}")
def read_item_handling_error(item_id: str):
    items = {"foo": "The Foo Wrestlers"}
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": items[item_id]}


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


@tutorial_app.post("/user_with_limited_response_model/", response_model=UserOut)
def create_user_with_limited_response_model(user: UserIn):
    return user


@tutorial_app.post("/user_in_fake_db/", response_model=UserOut)
def create_user_in_fake_db(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved


@tutorial_app.get("/models/{model_name}")
def get_model(model_name: ModelName):
    if model_name == ModelName.ALEXNET:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@tutorial_app.post("/file/")
def create_file(file: bytes = File(...)):
    return {"file_size": len(file)}


@tutorial_app.post("/uploadfile/")
def create_upload_file(
    file: UploadFile = File(..., description="A file read as UploadFile")
):
    """
    Using UploadFile has several advantages over bytes:
    You don't have to use File() in the default value of the parameter.
    It uses a "spooled" file:
    A file stored in memory up to a maximum size limit, and after passing this limit it will be stored in disk.
    This means that it will work well for large files like images, videos, large binaries, etc. without consuming all
    the memory.
    You can get metadata from the uploaded file.
    It has a file-like async interface.
    It exposes an actual Python SpooledTemporaryFile object that you can pass directly to other libraries that expect
    a file-like object.
    """
    return {"filename": file.filename}


@tutorial_app.post("/files/")
def create_files(files: List[bytes] = File(..., description="Multiple files as bytes")):
    return {"file_sizes": [len(file) for file in files]}


@tutorial_app.post("/uploadfiles/")
def create_upload_files(
    files: List[UploadFile] = File(..., description="Multiple files as UploadFile")
):
    return {"filenames": [file.filename for file in files]}


@tutorial_app.post("/file_and_form/")
def create_file_and_form(
    file: bytes = File(...), fileb: UploadFile = File(...), token: str = Form(...)
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }


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


@tutorial_app.post("/login/")
def login(username: str = Form(...)):
    return {"username": username}


@tutorial_app.get("/tags/", tags=[Tags.ENDPOINT_WITH_TAG_1])
def read_endpoint_with_tag():
    return {"username": "johndoe"}


@tutorial_app.get("/tags/{username}", tags=[Tags.ENDPOINT_WITH_TAG_1])
def read_endpoint_with_param_and_tag(username: str):
    return {"username": username}


@tutorial_app.get("/tags2/", tags=[Tags.ENDPOINT_WITH_TAG_2])
def read_endpoint_with_tag_2():
    return {"username": "johndoe2"}


@tutorial_app.post(
    "/pets/",
    response_model=Pet,
    summary="Create a pet",
    description="Create a pet with all the information, type and name",
)
def create_pet(pet: Pet):
    return pet


@tutorial_app.post(
    "/pets_docstring/",
    response_model=Pet,
    summary="Create a pet",
    response_description="The created pet",
)
def create_pet_docstring(pet: Pet):
    """
    Create a pet with all the information:

    - **type**: each pet must have a type, e.g: dog, cat, etc
    - **name**: each pet must have a name
    """
    return pet


@tutorial_app.get("/pets/", deprecated=True)
def read_pets():
    return [{"pet": "cat"}]


@tutorial_app.put("/item_with_datetime/{id}")
def update_item_with_datetime(id: str, item_with_datetime: ItemWithDatetime):
    fake_db = {}
    json_compatible_item_data = jsonable_encoder(item_with_datetime)
    fake_db[id] = json_compatible_item_data
    return json_compatible_item_data


@tutorial_app.exception_handler(UnicornException)
def unicorn_exception_handler(request: Request, exc: UnicornException):
    print(request, exc)
    return JSONResponse(
        status_code=status.HTTP_418_IM_A_TEAPOT,
        content={"message": f"Oops! {exc.name} did something. There goes a rainbow..."},
    )


@tutorial_app.get("/unicorns/{name}")
def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}


@tutorial_app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Override request validation exceptions to include what was sent as "body"
    """
    print(request, exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_active_user(current_user: AuthUser = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@tutorial_app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = AuthUserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@tutorial_app.get("/current_user")
def read_current_user(current_user: AuthUser = Depends(get_current_active_user)):
    return current_user


@tutorial_app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    A "middleware" is a function that works with every request before it is processed by any specific path operation.
     And also with every response before returning it.
    """
    start_time = t.time()
    response = await call_next(request)
    process_time = t.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
