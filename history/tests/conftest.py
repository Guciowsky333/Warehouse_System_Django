import pytest
from inventory.models import *
from users.models import *
@pytest.fixture
def test_location(db):
    return Location.objects.create(
        name="test_location",
    )

@pytest.fixture
def test_location2(db):
    return Location.objects.create(
        name="test_location2",
    )



@pytest.fixture
def test_component(db, test_location):
    return Component.objects.create(
        code="test_code",
        unique_code='test_unique_code',
        weight=10,
        quantity=500,
        location=test_location,
    )

@pytest.fixture
def test_user(db):
    return CustomUser.objects.create_user(
        username="test_username1",
        password="test_password1",
        first_name="test",
        last_name="user",
        role="test_role1",
    )