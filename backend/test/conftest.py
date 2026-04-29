import pytest
import time
import random
from fastapi.testclient import TestClient
from main import app

# Generate unique timestamp for each test run to avoid rate limiting
UNIQUE_ID = f"{int(time.time())}_{random.randint(1000, 9999)}"

def wait_if_rate_limited(client, method, url, json_data, max_retries=3):
    """Helper to retry requests if rate limited."""
    for i in range(max_retries):
        response = client.post(url, json=json_data) if method == "post" else None
        if response.status_code != 429:
            return response
        time.sleep(2)  # Wait longer for rate limit to reset
    return response

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

@pytest.fixture(scope="session")
def auth_headers(client):
    email = f"admin_{UNIQUE_ID}@gmail.com"
    password = "Admin@777"

    # Register with retry logic for rate limiting
    reg_data = {
        "email": email,
        "username": f"admin_{UNIQUE_ID}",
        "password": password,
        "role": "superadmin"
    }
    
    for i in range(3):
        reg_response = client.post("/auth/register", json=reg_data)
        if reg_response.status_code != 429:
            break
        time.sleep(2)

    # Wait before login (longer delay to avoid rate limit)
    time.sleep(2)
    
    # Login with retry
    login_data = {"email": email, "password": password}
    for i in range(3):
        response = client.post("/auth/login", json=login_data)
        if response.status_code != 429:
            break
        time.sleep(2)
    
    assert response.status_code == 200, f"Login failed: {response.json()}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def customer_id(client, auth_headers):
    unique = str(int(time.time()))
    response = client.post("/customers/", json={
        "name": "Test User",
        "age": 25,
        "gender": "male",
        "date_of_birth": "2000-01-01",
        "email": f"test_{unique}@test.com",
        "phone": "12345678",
        "company": "ABC",
        "job_title": "Engineer",
        "experience_years": 2,
        "customer_type": "regular",
        "status": "active"
    }, headers=auth_headers)
    
    assert response.status_code in [200, 201], f"Failed to create customer: {response.json()}"
    return response.json()["id"]
