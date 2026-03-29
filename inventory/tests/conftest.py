import pytest
from inventory.models import Location, Component, ReleasedComponent
from users.models import CustomUser
# fixtures
@pytest.fixture
def test_user(db):
    return CustomUser.objects.create_user(
        username="test_username1",
        password="test_password1",
        first_name="test_first_name1",
        last_name="test_last_name1",
        role="test_role1",
    )

@pytest.fixture
def test_location(db):
    return Location.objects.create(name="test_location")

@pytest.fixture
def test_location2(db):
    return Location.objects.create(name="test_location2")


@pytest.fixture
def test_component(db, test_location2):
    return Component.objects.create(
        code="test_component",
        unique_code="test_unique_code",
        location=test_location2,
        weight=20,
        quantity=1000,
    )
@pytest.fixture
def test_component2(db, test_location):
    return Component.objects.create(
        code="test_component2",
        unique_code="test_unique_code2",
        location=test_location,
        weight=25,
        quantity=500,
    )
@pytest.fixture
def test_released_component(db):
    return ReleasedComponent.objects.create(
        code="test_released_component",
        unique_code="test_released_unique_code",
        department="test_department",
        weight=20,
        quantity=1000,
    )

@pytest.fixture
def test_location_for_models(db):
    return Location.objects.create(name="test_location")


@pytest.fixture
def test_component_for_models(db, test_location_for_models):
    return Component.objects.create(
        code="test_component",
        location=test_location_for_models,
        weight=20,
        quantity=1000
    )
@pytest.fixture
def test_component2_for_models(db, test_location_for_models):
    return Component.objects.create(
        code="test_complement",
        location=test_location_for_models,
        weight=30,
        quantity=500,
    )