import pytest
from fastapi.testclient import TestClient

import os , sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from app import app
from database import db


client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    # Setup: Clear the test database
    db.users.delete_many({})
    db.notes.delete_many({})
    yield
    # Teardown: Clear the test database
    db.users.delete_many({})
    db.notes.delete_many({})

token = None
note_id = None
share_note_id = None

def test_signup():
    response = client.post("/api/auth/signup", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully"}

def test_signup_existing_user():
    response = client.post("/api/auth/signup", json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already registered"}

def test_login():
    global token
    response = client.post("/api/auth/login", data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    token = response.json()["access_token"]

def test_login_invalid_user():
    response = client.post("/api/auth/login", data={"username": "invaliduser", "password": "testpass"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid username or password"}

def test_create_note():
    global note_id
    response = client.post("/api/notes", json={"title": "Test Note", "content": "This is a test note."},
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Note created successfully"}

    # Retrieve the note from the database to get its ID
    note = db.notes.find_one({"title": "Test Note", "content": "This is a test note."})
    note_id = str(note["_id"])

def test_get_notes():
    response = client.get("/api/notes", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_note_by_id():
    response = client.get(f"/api/notes/{note_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["title"] == "Test Note"

def test_update_note():
    response = client.put(f"/api/notes/{note_id}", json={"title": "Updated Note", "content": "Updated content."},
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Note updated successfully"}

def test_delete_note():
    response = client.delete(f"/api/notes/{note_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Note deleted successfully"}

def test_share_note():
    global share_note_id
    # Create another user to share the note with
    response = client.post("/api/auth/signup", json={"username": "shareuser", "password": "sharepass"})
    assert response.status_code == 200
    assert response.json() == {"message": "User created successfully"}

    # Create a note to share
    response = client.post("/api/notes", json={"title": "Share Note", "content": "This is a share note."},
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    # Retrieve the note from the database to get its ID
    note = db.notes.find_one({"title": "Share Note", "content": "This is a share note."})
    share_note_id = str(note["_id"])

    # Share the note
    response = client.post(f"/api/notes/{share_note_id}/share", params={"username": "shareuser"},
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Note shared successfully"}

def test_search_notes():
    response = client.get("/api/search", params={"q": "share"},
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_rate_limiting():
    # Make 3 requests to trigger rate limiting
    for _ in range(3):
        response = client.get("/api/notes", headers={"Authorization": f"Bearer {token}"})
    
    # Last request should be rate limited
    assert response.status_code == 429
    assert response.json() == {"detail": "Too Many Requests"}