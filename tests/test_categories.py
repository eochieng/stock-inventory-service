def create_category(client, name="Beverages", description="Drinks"):
    return client.post("/categories/", json={"name": name, "description": description})


def test_create_category(client):
    response = create_category(client)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Beverages"
    assert body["description"] == "Drinks"
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_create_category_without_description(client):
    response = client.post("/categories/", json={"name": "Snacks"})

    assert response.status_code == 201
    assert response.json()["description"] is None


def test_create_category_duplicate_name_returns_409(client):
    create_category(client, name="Beverages")

    response = create_category(client, name="Beverages")

    assert response.status_code == 409
    assert response.json()["detail"] == "Category with this name already exists"


def test_create_category_missing_name_returns_422(client):
    response = client.post("/categories/", json={"description": "No name here"})

    assert response.status_code == 422


def test_create_category_blank_name_returns_422(client):
    response = client.post("/categories/", json={"name": ""})

    assert response.status_code == 422


def test_list_categories_empty(client):
    response = client.get("/categories/")

    assert response.status_code == 200
    assert response.json() == []


def test_list_categories_returns_created_categories_sorted_by_name(client):
    create_category(client, name="Snacks")
    create_category(client, name="Beverages")

    response = client.get("/categories/")

    assert response.status_code == 200
    names = [category["name"] for category in response.json()]
    assert names == ["Beverages", "Snacks"]


def test_list_categories_respects_skip_and_limit(client):
    for name in ("A", "B", "C", "D"):
        create_category(client, name=name)

    response = client.get("/categories/", params={"skip": 1, "limit": 2})

    assert response.status_code == 200
    names = [category["name"] for category in response.json()]
    assert names == ["B", "C"]
