

def test_register(client):
    response = client.post("/auth/register", json={
        "email": "user1@gmail.com",
        "username": "User",
        "password": "User@123",
        "role": "user"
    })
    assert response.status_code in [200, 201]


def test_login(client):
    client.post("/auth/register", json={
        "email": "user2@gmail.com",
        "username": "user2",
        "password": "User@123",
        "role": "user"
    })

    response = client.post("/auth/login", json={
        "email": "user2@gmail.com",
        "password": "User@123"
    })
    assert response.status_code == 200


def test_refresh(client, auth_headers):
    response = client.post("/auth/refresh", headers=auth_headers)
    assert response.status_code == 200


def test_get_users(client, auth_headers):
    response = client.get("/auth/users", headers=auth_headers)
    assert response.status_code == 200


def test_user_count(client, auth_headers):
    response = client.get("/auth/users/count", headers=auth_headers)
    assert response.status_code == 200