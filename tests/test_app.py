from copy import deepcopy

import pytest
from fastapi.testclient import TestClient


def test_root_redirects_to_static_page(client: TestClient):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_root_serves_static_page_after_redirect(client: TestClient):
    # Arrange
    expected_path = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=True)

    # Assert
    assert response.status_code == 200
    assert response.url.path == expected_path
    assert len(response.history) == 1
    assert response.headers["content-type"].startswith("text/html")
    assert "<html" in response.text.lower()


def test_get_activities_returns_complete_data(
    client: TestClient, isolated_activities
):
    # Arrange
    expected_activities = deepcopy(isolated_activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities
    assert isolated_activities == expected_activities


def test_activities_start_with_original_participants(client: TestClient):
    # Arrange
    expected_participants = [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == expected_participants


def test_signup_adds_participant(client: TestClient, isolated_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "test-student@mergington.edu"
    expected_activities = deepcopy(isolated_activities)
    expected_activities[activity_name]["participants"].append(email)

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert activities_response.status_code == 200
    assert activities_response.json() == expected_activities
    assert isolated_activities == expected_activities
    assert isolated_activities[activity_name]["participants"].count(email) == 1


def test_signup_rejects_duplicate_participant(
    client: TestClient, isolated_activities
):
    # Arrange
    activity_name = "Chess Club"
    email = isolated_activities[activity_name]["participants"][0]
    expected_activities = deepcopy(isolated_activities)

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert isolated_activities == expected_activities


@pytest.mark.parametrize("method", ["POST", "DELETE"])
def test_signup_rejects_unknown_activity(
    client: TestClient, isolated_activities, method: str
):
    # Arrange
    expected_activities = deepcopy(isolated_activities)
    email = "test-student@mergington.edu"

    # Act
    response = client.request(
        method, "/activities/Unknown Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert isolated_activities == expected_activities


def test_unregister_removes_only_requested_participant(
    client: TestClient, isolated_activities
):
    # Arrange
    activity_name = "Chess Club"
    email = isolated_activities[activity_name]["participants"][0]
    expected_activities = deepcopy(isolated_activities)
    expected_activities[activity_name]["participants"].remove(email)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert activities_response.status_code == 200
    assert activities_response.json() == expected_activities
    assert isolated_activities == expected_activities


def test_unregister_rejects_nonparticipant(
    client: TestClient, isolated_activities
):
    # Arrange
    expected_activities = deepcopy(isolated_activities)
    email = "not-registered@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert isolated_activities == expected_activities


@pytest.mark.parametrize("method", ["POST", "DELETE"])
def test_signup_requires_email(
    client: TestClient, isolated_activities, method: str
):
    # Arrange
    expected_activities = deepcopy(isolated_activities)

    # Act
    response = client.request(method, "/activities/Chess Club/signup")

    # Assert
    assert response.status_code == 422
    assert any(
        error["loc"] == ["query", "email"] and error["type"] == "missing"
        for error in response.json()["detail"]
    )
    assert isolated_activities == expected_activities
