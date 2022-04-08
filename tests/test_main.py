from fastapi.testclient import TestClient

from main import tutorial_app

client = TestClient(tutorial_app)


def test_read_items():
    response = client.get("/items")
    print(response)
    assert response.status_code == 200
    assert response.json() == [
        {"item_name": "Foo"},
        {"item_name": "Bar"},
        {"item_name": "Baz"},
    ]
