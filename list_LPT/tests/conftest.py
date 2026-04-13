import pytest
from inventory.models import *
from users.models import *
from list_LPT.models import *




@pytest.fixture
def test_warehouseman(db):
    return CustomUser.objects.create_user(
        username="test_username3",
        password="test_password3",
        first_name="test_first_name3",
        last_name="test_last_name3",
        role="warehouseman",
    )


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
    return Location.objects.create(name='A10101')

@pytest.fixture
def test_location2(db):
    return Location.objects.create(name='A10102')


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
@pytest.fixture
def test_component_on_list(db, test_location, test_list_lpt):
    return Component.objects.create(
        code= 'test_code',
        unique_code ='unique_code_1',
        quantity = 1000,
        weight = 10,
        location = test_location,
        list=test_list_lpt,
    )

@pytest.fixture
def test_component_off_list(db, test_location, test_list_lpt):
    return Component.objects.create(
        code= 'test_code',
        unique_code ='unique_code_2',
        quantity = 1000,
        weight = 10,
        location = test_location,
    )




@pytest.fixture
def test_list_lpt(db, test_user_foreman):
    return ListLPT.objects.create(
        list_number='number_1',
        user=test_user_foreman,
        department='5000'
    )

@pytest.fixture
def test_list_lpt_closed(db, test_user_foreman):
    return ListLPT.objects.create(
        list_number='number_2',
        user=test_user_foreman,
        department='5000',
        closed = True
    )

@pytest.fixture
def test_location_A10101(db):
    return Location.objects.create(name='A10101')

@pytest.fixture
def test_location_A10102(db):
    return Location.objects.create(name='A10102')

@pytest.fixture
def test_location_B12103(db):
    return Location.objects.create(name='B12103')
