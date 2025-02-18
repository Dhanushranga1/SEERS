import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.models.user import User
from app.core.auth import hash_password
from sqlalchemy.orm import Session

client = TestClient(app)

# Dependency override to use a test database
def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[Session] = override_get_db

# Test User Data
test_user = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
}

@pytest.fixture(scope="module")
def setup_test_db():
    """Setup test database with a clean state"""
    db = SessionLocal()
    
    # Ensure clean DB state before each test
    db.query(User).delete()
    db.commit()
    
    yield db
    db.close()

# ✅ Test User Registration
def test_register_user(setup_test_db):
    response = client.post("/auth/register", json=test_user)
    assert response.status_code == 201
    assert response.json() == {"message": "User registered successfully"}

# ✅ Test Duplicate Registration (should fail)
def test_register_duplicate_user(setup_test_db):
    response = client.post("/auth/register", json=test_user)
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}

# ✅ Test Login with Correct Credentials
def test_login_user(setup_test_db):
    response = client.post("/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

# ✅ Test Login with Incorrect Password
def test_login_invalid_password(setup_test_db):
    response = client.post("/auth/login", json={
        "email": test_user["email"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}

# ✅ Test Login with Non-Existent User
def test_login_non_existent_user(setup_test_db):
    response = client.post("/auth/login", json={
        "email": "doesnotexist@example.com",
        "password": "randompassword"
    })
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}
