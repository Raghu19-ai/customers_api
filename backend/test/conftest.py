import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    email = "admin@gmail.com"
    password = "Admin@777"

    # Register
    client.post("/auth/register", json={
        "email": email,
        "username": "admin",
        "password": password,
        "role": "superadmin"
    })

    # Login
    response = client.post("/auth/login", json={
        "email": email,
        "password": password
    })

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def customer_id(client, auth_headers):
    response = client.post("/customers/", json={
        "name": "Test User",
        "age": 25,
        "gender": "male",
        "date_of_birth": "2000-01-01",
        "email": "test@test.com",
        "phone": "12345678",
        "company": "ABC",
        "job_title": "Engineer",
        "experience_years": 2,
        "customer_type": "regular",
        "status": "active"
    }, headers=auth_headers)

    return response.json()["id"]
