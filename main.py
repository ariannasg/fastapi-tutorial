from fastapi import FastAPI

from models import ModelName

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


@app.get("/users/me")
def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
def read_user(user_id: str):
    return {"user_id": user_id}


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
