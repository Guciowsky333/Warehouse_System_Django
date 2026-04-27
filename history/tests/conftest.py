import pytest

from history.models import ComponentHistory
from inventory.models import *
from users.models import *
@pytest.fixture
def test_location(db):
    return Location.objects.create(
        name="A10101",
    )

@pytest.fixture
def test_location2(db):
    return Location.objects.create(
        name="A10102",
    )



@pytest.fixture
def test_component(db, test_location):
    return Component.objects.create(
        code="code",
        unique_code='unique_code',
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

@pytest.fixture
def test_history_component_release(db, test_component, test_user, test_location):
    return ComponentHistory.objects.create(
        action='component_release',
        code = test_component.code,
        unique_code = test_component.unique_code,
        weight = test_component.weight,
        quantity = test_component.quantity,
        user = test_user,
        full_name = test_user.full_name(),
        previous_location = test_location.name,
        current_location = '5000'
    )