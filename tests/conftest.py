"""Shared HTTP client and isolated in-memory activity state."""

from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def activity_snapshot():
    """Restore the existing dictionary in place, even when a test fails."""
    original = deepcopy(activities)
    try:
        yield original
    finally:
        activities.clear()
        activities.update(original)


@pytest.fixture
def client(activity_snapshot):
    """Close the HTTP client before the activity state is restored."""
    with TestClient(app) as test_client:
        yield test_client