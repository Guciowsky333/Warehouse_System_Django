import pytest
from inventory.models import *
from users.models import *

@pytest.fixture
def test_user_foreman(db):
    return CustomUser.objects.create_user(
        username="test_username1",
        password="test_password1",
        first_name="test_first_name1",
        last_name="test_last_name1",
        role="foreman",
    )
@pytest.fixture
def test_user_warehouseman(db):
    return CustomUser.objects.create_user(
        username="test_username1",
        password="test_password1",
        first_name="test_first_name1",
        last_name="test_last_name1",
        role="warehouseman",
    )


@pytest.fixture
def test_location(db):
    return Location.objects.create(name='test_location')

@pytest.fixture
def test_location2(db):
    return Location.objects.create(name='test_location2')


@pytest.fixture
def test_components_15016610(db, test_location):
    component_15016610_1 = Component.objects.create(
        code='15016610',
        weight=20,
        quantity=1000,
        location=test_location,
    )
    component_15016610_2 = Component.objects.create(
        code='15016610',
        weight=20,
        quantity=1000,
        location=test_location,
    )

    component_15016610_3 = Component.objects.create(
        code='15016610',
        weight=20,
        quantity=1000,
        location=test_location,
    )


    return component_15016610_1, component_15016610_2, component_15016610_3


@pytest.fixture
def test_components_15016812(db, test_location):
    component_15016812_1 = Component.objects.create(
        code='15016812',
        weight=4,
        quantity=210,
        location=test_location,
    )
    component_15016812_2 = Component.objects.create(
        code='15016812',
        weight=10,
        quantity=500,
        location=test_location,
    )

    component_15016812_3 = Component.objects.create(
        code='15016812',
        weight=10,
        quantity=500,
        location=test_location,
    )

    return component_15016812_1, component_15016812_2, component_15016812_3

@pytest.fixture
def test_components_15016808(db, test_location):
    component_15016808_1 = Component.objects.create(
        code='15016808',
        weight=10,
        quantity=1000,
        location=test_location,
    )
    component_15016808_2 = Component.objects.create(
        code='15016808',
        weight=10,
        quantity=1000,
        location=test_location,
    )

    return component_15016808_1, component_15016808_2