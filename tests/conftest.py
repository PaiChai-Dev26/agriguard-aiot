from uuid import uuid4

import pytest


@pytest.fixture
def incident_id():
    return uuid4()

