"""
Tests for the FastAPI backend application.
"""

from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test GET /activities returns the activity dictionary."""
    # Arrange: No special setup needed for this endpoint

    # Act: Make the GET request
    response = client.get("/activities")

    # Assert: Check status and response content
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data  # Example activity exists
    assert "participants" in data["Chess Club"]


def test_signup_success():
    """Test successful signup for an activity."""
    # Arrange: Prepare signup data
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act: Make the POST request
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert: Check success response and participant added
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]

    # Verify participant was added by checking GET /activities
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate():
    """Test duplicate signup returns 400 and doesn't add twice."""
    # Arrange: Sign up once first
    activity_name = "Programming Class"
    email = "duplicate@mergington.edu"
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Act: Try to sign up again
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert: Check 400 response and participant not duplicated
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]

    # Verify only one instance in participants
    response = client.get("/activities")
    activities = response.json()
    assert activities[activity_name]["participants"].count(email) == 1


def test_remove_participant_success():
    """Test successful removal of a participant."""
    # Arrange: Add a participant first
    activity_name = "Gym Class"
    email = "removeme@mergington.edu"
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Act: Remove the participant
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )

    # Assert: Check success response and participant removed
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]

    # Verify participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_not_found():
    """Test removing a nonexistent participant returns 404."""
    # Arrange: Activity and email that doesn't exist
    activity_name = "Chess Club"
    email = "nonexistent@mergington.edu"

    # Act: Try to remove
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )

    # Assert: Check 404 response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]