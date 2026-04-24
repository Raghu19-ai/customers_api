def test_create_address(client, auth_headers, customer_id):
    response = client.post("/addresses/", json={
        "customer_id": customer_id,
        "city": "Bangalore",
        "state": "KA",
        "pincode": "560001"
    }, headers=auth_headers)

    assert response.status_code == 200