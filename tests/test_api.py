def signup(client, email="morgan@example.com", password="correct-horse-42"):
    return client.post(
        "/auth/signup",
        json={"name": "Morgan Lee", "email": email, "password": password},
    )


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_user_signup(client):
    response = signup(client)

    assert response.status_code == 201
    body = response.json()
    assert body["user"]["name"] == "Morgan Lee"
    assert body["user"]["email"] == "morgan@example.com"
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


def test_duplicate_email_registration_is_rejected(client):
    assert signup(client).status_code == 201

    duplicate = signup(client, email="MORGAN@example.com")

    assert duplicate.status_code == 409


def test_successful_login(client):
    signup(client)

    response = client.post(
        "/auth/login",
        json={"email": "MORGAN@example.com", "password": "correct-horse-42"},
    )

    assert response.status_code == 200
    assert response.json()["user"]["email"] == "morgan@example.com"
    assert response.json()["access_token"]


def test_invalid_login_is_rejected(client):
    signup(client)

    response = client.post(
        "/auth/login",
        json={"email": "morgan@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_jwt_authentication_and_protected_profile(client):
    created = signup(client).json()
    token = created["access_token"]

    missing_auth = client.get("/auth/me")
    valid_auth = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    invalid_auth = client.get(
        "/auth/me", headers={"Authorization": "Bearer not-a-valid-jwt"}
    )

    assert missing_auth.status_code == 401
    assert valid_auth.status_code == 200
    assert valid_auth.json() == {
        "id": created["user"]["id"],
        "name": "Morgan Lee",
        "email": "morgan@example.com",
    }
    assert invalid_auth.status_code == 401
