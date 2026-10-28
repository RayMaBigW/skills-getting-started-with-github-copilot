"""Regression tests for participant unregistration."""

from copy import deepcopy
import unittest

from fastapi.testclient import TestClient

from src.app import activities, app


class UnregisterTests(unittest.TestCase):
    def setUp(self):
        self.original_activities = deepcopy(activities)
        self.client = TestClient(app)

    def tearDown(self):
        activities.clear()
        activities.update(self.original_activities)
        self.client.close()

    def test_unregister_removes_only_selected_participant(self):
        response = self.client.delete(
            "/activities/Chess%20Club/signup",
            params={"email": "michael@mergington.edu"},
        )
        self.assertEqual(response.status_code, 200)
        participants = self.client.get("/activities").json()["Chess Club"]["participants"]
        self.assertEqual(participants, ["daniel@mergington.edu"])

    def test_unregister_unknown_activity(self):
        response = self.client.delete(
            "/activities/Unknown/signup", params={"email": "michael@mergington.edu"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(activities, self.original_activities)

    def test_unregister_missing_participant(self):
        response = self.client.delete(
            "/activities/Chess%20Club/signup", params={"email": "missing@mergington.edu"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(activities, self.original_activities)

    def test_participant_can_register_again_after_removal(self):
        endpoint = "/activities/Chess%20Club/signup"
        params = {"email": "michael@mergington.edu"}
        self.assertEqual(self.client.delete(endpoint, params=params).status_code, 200)
        self.assertEqual(self.client.delete(endpoint, params=params).status_code, 404)
        self.assertEqual(self.client.post(endpoint, params=params).status_code, 200)
        self.assertEqual(activities["Chess Club"]["participants"].count(params["email"]), 1)