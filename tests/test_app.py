"""Backend listing, redirect, signup, and validation tests using AAA."""

from copy import deepcopy

import pytest

from src.app import activities


def test_root_redirects_to_static_page(client, activity_snapshot):
    # Arrange
    endpoint = "/"

    # Act
    response = client.get(endpoint, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"
    assert activities == activity_snapshot


def test_get_activities_returns_expected_data_without_mutation(client, activity_snapshot):
    # Arrange
    endpoint = "/activities"

    # Act
    response = client.get(endpoint)

    # Assert
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    data = response.json()
    assert data == activity_snapshot
    assert "Chess Club" in data
    for name, details in data.items():
        assert isinstance(name, str)
        assert isinstance(details["description"], str)
        assert isinstance(details["schedule"], str)
        assert isinstance(details["max_participants"], int)
        assert isinstance(details["participants"], list)
        assert all(isinstance(email, str) for email in details["participants"])
    assert activities == activity_snapshot


def test_signup_adds_one_participant_visible_in_listing(client, activity_snapshot):
    # Arrange
    email = "new+student@mergington.edu"
    expected = deepcopy(activity_snapshot)
    expected["Chess Club"]["participants"].append(email)

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})
    listing = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert listing.status_code == 200
    assert listing.json() == expected
    assert listing.json()["Chess Club"]["participants"].count(email) == 1
    assert activities == expected


def test_duplicate_signup_is_rejected_without_mutation(client, activity_snapshot):
    # Arrange
    email = activity_snapshot["Chess Club"]["participants"][0]

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert activities == activity_snapshot


def test_signup_unknown_activity_is_rejected_without_mutation(client, activity_snapshot):
    # Arrange
    endpoint = "/activities/Unknown/signup"
    params = {"email": "new@mergington.edu"}

    # Act
    response = client.post(endpoint, params=params)

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activities == activity_snapshot


@pytest.mark.parametrize("method", ["POST", "DELETE"])
def test_signup_endpoints_require_email(client, activity_snapshot, method):
    # Arrange
    endpoint = "/activities/Chess%20Club/signup"

    # Act
    response = client.request(method, endpoint)

    # Assert
    assert response.status_code == 422
    assert any(
        error["loc"] == ["query", "email"] and error["type"] == "missing"
        for error in response.json()["detail"]
    )
    assert activities == activity_snapshot