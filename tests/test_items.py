def create_category(client, name="Beverages"):
    response = client.post("/categories/", json={"name": name})
    assert response.status_code == 201
    return response.json()


def create_item(client, category_id, sku="BEV-001", name="Cola 12oz", **overrides):
    payload = {
        "sku": sku,
        "name": name,
        "quantity": 100,
        "unit_price": "1.50",
        "category_id": category_id,
    }
    payload.update(overrides)
    return client.post("/items/", json=payload)


def test_create_item(client):
    category = create_category(client)

    response = create_item(client, category["id"])

    assert response.status_code == 201
    body = response.json()
    assert body["sku"] == "BEV-001"
    assert body["name"] == "Cola 12oz"
    assert body["quantity"] == 100
    assert body["unit_price"] == "1.50"
    assert body["category"]["id"] == category["id"]
    assert body["category"]["name"] == category["name"]


def test_create_item_defaults_quantity_to_zero(client):
    category = create_category(client)

    response = client.post(
        "/items/",
        json={
            "sku": "BEV-002",
            "name": "Sparkling Water",
            "unit_price": "2.00",
            "category_id": category["id"],
        },
    )

    assert response.status_code == 201
    assert response.json()["quantity"] == 0


def test_create_item_with_missing_category_returns_404(client):
    response = create_item(client, category_id=999)

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_create_item_with_duplicate_sku_returns_409(client):
    category = create_category(client)
    create_item(client, category["id"], sku="BEV-001")

    response = create_item(client, category["id"], sku="BEV-001", name="Another Cola")

    assert response.status_code == 409
    assert response.json()["detail"] == "Item with this SKU already exists"


def test_create_item_with_negative_quantity_returns_422(client):
    category = create_category(client)

    response = create_item(client, category["id"], quantity=-1)

    assert response.status_code == 422


def test_create_item_with_negative_price_returns_422(client):
    category = create_category(client)

    response = create_item(client, category["id"], unit_price="-1.00")

    assert response.status_code == 422


def test_create_item_with_missing_required_field_returns_422(client):
    category = create_category(client)

    response = client.post(
        "/items/",
        json={"sku": "BEV-003", "category_id": category["id"]},
    )

    assert response.status_code == 422


def test_list_items_empty(client):
    response = client.get("/items/")

    assert response.status_code == 200
    assert response.json() == []


def test_list_items_returns_created_items_sorted_by_name(client):
    category = create_category(client)
    create_item(client, category["id"], sku="BEV-002", name="Water")
    create_item(client, category["id"], sku="BEV-001", name="Cola")

    response = client.get("/items/")

    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert names == ["Cola", "Water"]


def test_list_items_filters_by_category_id(client):
    beverages = create_category(client, name="Beverages")
    snacks = create_category(client, name="Snacks")
    create_item(client, beverages["id"], sku="BEV-001", name="Cola")
    create_item(client, snacks["id"], sku="SNK-001", name="Chips")

    response = client.get("/items/", params={"category_id": beverages["id"]})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["sku"] == "BEV-001"


def test_list_items_respects_skip_and_limit(client):
    category = create_category(client)
    for i in range(4):
        create_item(client, category["id"], sku=f"SKU-{i}", name=f"Item {i}")

    response = client.get("/items/", params={"skip": 1, "limit": 2})

    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert names == ["Item 1", "Item 2"]


def test_get_item(client):
    category = create_category(client)
    created = create_item(client, category["id"]).json()

    response = client.get(f"/items/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["sku"] == "BEV-001"


def test_get_item_not_found_returns_404(client):
    response = client.get("/items/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_update_item_quantity(client):
    category = create_category(client)
    created = create_item(client, category["id"]).json()

    response = client.patch(f"/items/{created['id']}", json={"quantity": 42})

    assert response.status_code == 200
    body = response.json()
    assert body["quantity"] == 42
    assert body["sku"] == created["sku"]
    assert body["name"] == created["name"]


def test_update_item_partial_update_leaves_other_fields_unchanged(client):
    category = create_category(client)
    created = create_item(client, category["id"], name="Cola 12oz").json()

    response = client.patch(f"/items/{created['id']}", json={"name": "Cola 16oz"})

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Cola 16oz"
    assert body["quantity"] == created["quantity"]
    assert body["unit_price"] == created["unit_price"]


def test_update_item_category(client):
    beverages = create_category(client, name="Beverages")
    snacks = create_category(client, name="Snacks")
    created = create_item(client, beverages["id"]).json()

    response = client.patch(f"/items/{created['id']}", json={"category_id": snacks["id"]})

    assert response.status_code == 200
    assert response.json()["category"]["id"] == snacks["id"]


def test_update_item_with_missing_category_returns_404(client):
    category = create_category(client)
    created = create_item(client, category["id"]).json()

    response = client.patch(f"/items/{created['id']}", json={"category_id": 999})

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


def test_update_item_not_found_returns_404(client):
    response = client.patch("/items/999", json={"quantity": 5})

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_update_item_with_negative_quantity_returns_422(client):
    category = create_category(client)
    created = create_item(client, category["id"]).json()

    response = client.patch(f"/items/{created['id']}", json={"quantity": -5})

    assert response.status_code == 422
