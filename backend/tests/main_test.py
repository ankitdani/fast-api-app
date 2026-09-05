from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
import models
import pytest

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_only.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestSessionLocal = sessionmaker(
    bind=engine
)

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# models.Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)

def test_register_user():
    response = client.post("/users/register", json={"username": "test user 1", "password": "1234"})
    assert response.status_code == 200
    assert response.json()["username"] == "test user 1"

def test_register_duplicate_user():
    response = client.post("/users/register", json={"username": "test user 1", "password": "1234"})
    assert response.status_code == 200

    response = client.post("/users/register", json={"username": "test user 1", "password": "1234"})
    assert response.status_code == 400

def test_login_succees():
    response = client.post("/users/register", json={"username": "test user 2", "password": "1234"})
    assert response.status_code == 200

    response = client.post("/users/login", data={"username": "test user 2", "password": "1234"})
    assert response.status_code == 200

def test_wrong_password():
    response = client.post("/users/register", json={"username": "test user 3", "password": "1234"})
    assert response.status_code == 200

    response = client.post("/users/login", data={"username": "test user 3", "password": "12345"})
    assert response.status_code == 401

def test_create_item_without_token():
    response = client.post("/items/", json={"name": "item 1 name", "description": "item 1 description"})
    assert response.status_code == 401

def test_create_item_with_token():
    response = client.post("/users/register", json={"username": "test user 2", "password": "1234"})
    assert response.status_code == 200

    response = client.post("/users/login", data={"username": "test user 2", "password": "1234"})
    assert response.status_code == 200

    token = response.json()["access_token"]
    item_response = client.post(
        "/items/", 
        json={"name": "item 1 name", "description": "item 1 description"},
        headers={"Authorization": f"Bearer {token}"})
    assert item_response.status_code == 200

def test_delete_item():
    response = client.post("/users/register", json={"username": "test user", "password": "1234"})
    assert response.status_code == 200

    response = client.post("/users/login", data={"username": "test user", "password": "1234"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    item_response = client.post(
        "/items/", 
        json={"name": "item 1", "description": "item 1 description"},
        headers={"Authorization": f"Bearer {token}"})
    assert item_response.status_code == 200
    
    item_id = item_response.json()["id"]
    response = client.delete(
        f"/items/{item_id}", 
        headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_delete_other_items():
    response1 = client.post("/users/register", json={"username": "test user 1", "password": "1234"})
    assert response1.status_code == 200

    response = client.post("/users/register", json={"username": "test user 2", "password": "1234"})
    assert response.status_code == 200

    response1 = client.post("/users/login", data={"username": "test user 1", "password": "1234"})
    assert response1.status_code == 200
    token1 = response1.json()["access_token"]

    response = client.post("/users/login", data={"username": "test user 2", "password": "1234"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    item_response1 = client.post(
        "/items/", 
        json={"name": "item 1", "description": "item 1 description"},
        headers={"Authorization": f"Bearer {token1}"})
    assert item_response1.status_code == 200
    
    item_id = item_response1.json()["id"]
    response = client.delete(
        f"/items/{item_id}", 
        headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

def test_update_item():
    response = client.post("/users/register", json={"username": "test user", "password": "1234"})
    assert response.status_code == 200

    response = client.post("/users/login", data={"username": "test user", "password": "1234"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    item_response = client.post(
        "/items/", 
        json={"name": "item 1", "description": "item 1 description"},
        headers={"Authorization": f"Bearer {token}"})
    assert item_response.status_code == 200
    
    item_id = item_response.json()["id"]
    response = client.put(
        f"/items/{item_id}", 
        json={"name": "item name 1 updated", "description": "item 1 description updated"},
        headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200