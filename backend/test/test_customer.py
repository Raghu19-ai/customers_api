def test_create_customer(client, auth_headers):
    response = client.post("/customers/", json={
        "name": "Shreyas",
        "age": 25,
        "gender": "male",
        "date_of_birth": "2000-01-01",
        "email": "cust@test.com",
        "phone": "12345678",
        "company": "ABC",
        "job_title": "Engineer",
        "experience_years": 2,
        "customer_type": "regular",
        "status": "active"
    }, headers=auth_headers)

    assert response.status_code == 200


def test_get_customers(client, auth_headers):
    response = client.get("/customers/", headers=auth_headers)
    assert response.status_code == 200


def test_update_customer(client, auth_headers, customer_id):
    response = client.put(f"/customers/{customer_id}", json={
        "name": "Updated",
        "age": 26,
        "gender": "male",
        "date_of_birth": "1999-01-01",
        "email": "updated@test.com",
        "phone": "99999999",
        "company": "XYZ",
        "job_title": "Senior Engineer",
        "experience_years": 3,
        "customer_type": "premium",
        "status": "active"
    }, headers=auth_headers)

    assert response.status_code == 200


def test_delete_customer(client, auth_headers, customer_id):
    response = client.delete(f"/customers/{customer_id}", headers=auth_headers)
    assert response.status_code == 200