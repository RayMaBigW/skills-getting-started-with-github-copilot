"""Regression tests for participant unregistration using AAA."""

from copy import deepcopy

from src.app import activities


def test_unregister_removes_only_selected_participant(client, activity_snapshot):
    # Arrange
    email = activity_snapshot["Chess Club"]["participants"][0]
    expected = deepcopy(activity_snapshot)
    expected["Chess Club"]["participants"].remove(email)

    # Act
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})
    listing = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert listing.status_code == 200
    assert listing.json() == expected
    assert activities == expected


def test_unregister_unknown_activity(client, activity_snapshot):
    # Arrange
    endpoint = "/activities/Unknown/signup"
    params = {"email": "michael@mergington.edu"}

    # Act
    response = client.delete(endpoint, params=params)

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activities == activity_snapshot


def test_unregister_missing_participant(client, activity_snapshot):
    # Arrange
    endpoint = "/activities/Chess%20Club/signup"
    params = {"email": "missing@mergington.edu"}

    # Act
    response = client.delete(endpoint, params=params)

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not registered for this activity"}
    assert activities == activity_snapshot


def test_repeated_unregister_is_rejected_without_mutation(client, activity_snapshot):
    # Arrange
    endpoint = "/activities/Chess%20Club/signup"
    email = activity_snapshot["Chess Club"]["participants"][0]
    params = {"email": email}
    initial_removal = client.delete(endpoint, params=params)
    expected = deepcopy(activity_snapshot)
    expected["Chess Club"]["participants"].remove(email)

    # Act
    response = client.delete(endpoint, params=params)

    # Assert
    assert initial_removal.status_code == 200
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not registered for this activity"}
    assert activities == expected


def test_participant_can_register_again_after_removal(client, activity_snapshot):
    # Arrange
    endpoint = "/activities/Chess%20Club/signup"
    email = activity_snapshot["Chess Club"]["participants"][0]
    params = {"email": email}
    initial_removal = client.delete(endpoint, params=params)
    expected = deepcopy(activity_snapshot)
    expected["Chess Club"]["participants"].remove(email)
    expected["Chess Club"]["participants"].append(email)

    # Act
    response = client.post(endpoint, params=params)
    listing = client.get("/activities")

    # Assert
    assert initial_removal.status_code == 200
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert listing.status_code == 200
    assert listing.json() == expected
    assert activities == expected
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_unregister_last_participant_leaves_empty_list(client, activity_snapshot):
    # Arrange
    email = "last@mergington.edu"
    activities["Chess Club"]["participants"] = [email]
    expected = deepcopy(activity_snapshot)
    expected["Chess Club"]["participants"] = []

    # Act
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})
    listing = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert listing.status_code == 200
    assert listing.json()["Chess Club"]["participants"] == []
    assert listing.json() == expected
    assert activities == expected