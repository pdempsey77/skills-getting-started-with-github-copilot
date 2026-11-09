from collections.abc import Iterator
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture(autouse=True)
def isolated_activities(monkeypatch: pytest.MonkeyPatch):
    activities = deepcopy(app_module.activities)
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(isolated_activities) -> Iterator[TestClient]:
    with TestClient(app_module.app) as test_client:
        yield test_client
