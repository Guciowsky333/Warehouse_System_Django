import pytest
from inventory.models import Location, Component, ReleasedComponent
from users.models import CustomUser
from rest_framework import status
from rest_framework.test import APIClient


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

# test for /api/inventory/change_location/
@pytest.mark.parametrize(
    'payload, expected_status', [

        # User provided empty unique_code or location
        ({'unique_code':'', 'location':''}, status.HTTP_400_BAD_REQUEST),
        # User provided unique code that dont exist
        ({'unique_code':'wrong_unique_code', 'location':'test_location'}, status.HTTP_404_NOT_FOUND),
        # User provided location that dont exist
        ({'unique_code':'test_unique_code', 'location':'wrong_location'}, status.HTTP_404_NOT_FOUND),
        # User provided unique code that has been already released to production
        ({'unique_code':'test_released_unique_code', 'location':'wrong_location'}, status.HTTP_400_BAD_REQUEST),
        # Appropriate data
        ({'unique_code':'test_unique_code', 'location':'test_location'}, status.HTTP_200_OK),
    ]
)

def test_ChangeLocationView(payload, expected_status, test_component, test_location, test_user, test_released_component):
    client = APIClient()
    client.force_authenticate(test_user)

    response = client.patch('/api/inventory/change_location/', payload, format='json')

    assert response.status_code == expected_status


    # checking if our test component has been added to our test location correctly
    if expected_status == status.HTTP_200_OK:
        assert test_location.components.filter(unique_code="test_unique_code").exists()

def test_ChangeLocationView_requires_authentication():
    client = APIClient()
    response = client.get('/api/inventory/change_location/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_ChangeLocationView_max_weight(test_location, test_component, test_user):
    """In this test we assigned to our test location component that weighs 790 kg
    so now we shouldn't be albe to add our test component that weighs 20 kg to this location
    because each location can't exceed 800 kg"""


    client = APIClient()
    client.force_authenticate(test_user)



    Component.objects.create(
        code="heavy_component",
        unique_code="heavy_unique_code",
        location=test_location,
        weight=790,
        quantity=1000,
    )

    test_location.refresh_from_db()

    body = {
        'unique_code': 'test_unique_code',
        'location': 'test_location'
    }

    response = client.patch('/api/inventory/change_location/', body, format='json')


    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Checking if the total_weight of our location is still 790 kg
    assert test_location.total_weight == 790

    # Checking whether the test component not has been added to our test location as we expected
    assert not test_location.components.filter(unique_code='test_unique_code').exists()





