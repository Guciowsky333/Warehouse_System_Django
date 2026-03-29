import pytest
from inventory.models import Location, Component, ReleasedComponent
from inventory.tests.test_models import test_component_unique_code
from users.models import CustomUser
from rest_framework import status
from rest_framework.test import APIClient


# test for /api/inventory/change_location/
@pytest.mark.parametrize(
    'payload, expected_status', [

        # User provided empty unique_code
        ({'unique_code':'', 'location':'test_location'}, status.HTTP_400_BAD_REQUEST),
        # User provided empty location
        ({'unique_code':'test_unique_code', 'location':''}, status.HTTP_400_BAD_REQUEST),
        # User provided unique code that dont exist
        ({'unique_code':'wrong_unique_code', 'location':'test_location'}, status.HTTP_404_NOT_FOUND),
        # User provided location that dont exist
        ({'unique_code':'test_unique_code', 'location':'wrong_location'}, status.HTTP_404_NOT_FOUND),
        # Status "4" means - User provided unique code that has been already released to production
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





# Test for /api/inventory/release_component/
@pytest.mark.parametrize(
    'payload, expected_status', [
        # Empty unique code
        ({'unique_code':'', 'department':'5500'}, status.HTTP_400_BAD_REQUEST),
        # Empty department
        ({'unique_code':'test_unique_code', 'department':''}, status.HTTP_400_BAD_REQUEST),
        # User provided wrong department allows [5000, 5500, 5800, 6000]
        ({'unique_code':'test_unique_code', 'department':'wrong_department'}, status.HTTP_400_BAD_REQUEST),
        # Status "4" means - User provided unique code that has been already released to production
        ({'unique_code':'test_released_unique_code', 'department':'5500'}, status.HTTP_400_BAD_REQUEST),
        # User provided unique code that not belong to any components
        ({'unique_code':'wrong_unique_code', 'department':'5500'}, status.HTTP_404_NOT_FOUND),
        # Appropriate data
        ({'unique_code':'test_unique_code', 'department':'5500'}, status.HTTP_201_CREATED),

    ]
)

def test_ReleasedComponentView(payload, expected_status, test_component, test_released_component, test_user):
    client = APIClient()
    client.force_authenticate(test_user)

    # We are taking a unique code of our component before request to then check if it will be removed correctly
    unique_code = test_component.unique_code

    response = client.post('/api/inventory/release_component/', payload, format='json')
    assert response.status_code == expected_status

    if expected_status == status.HTTP_201_CREATED:

        # Checking if our component has been removed from warehouse
        assert not Component.objects.filter(unique_code=unique_code).exists()

        # Checking if model ReleasedComponent with the same unique code and provided department has been created correctly
        assert ReleasedComponent.objects.filter(unique_code=unique_code, department=payload['department']).exists()


def test_ReleasedComponentView_requires_authentication():
    client = APIClient()
    response = client.get('/api/inventory/release_component/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test for /api/inventory/check_location/
@pytest.mark.parametrize(
    'location, expected_status', [
        # Empty location
        ('', status.HTTP_400_BAD_REQUEST),
        # Not exist location
        ('wrong_location', status.HTTP_404_NOT_FOUND),
        # Appropriate data
        ('test_location', status.HTTP_200_OK),
    ]
)

def test_CheckLocationView(location, expected_status, test_location, test_user):
    """First we are creating 3 components with our location to check if endpoint will return them to us in appropriate way.
    The first one and the second will be with the same code so we expect that quantity of components with the same code
    will be totaled, and they will be return as a one code with totaled quantity.
    So the endpoint should return 2 components, the first and second as one and the third with different code"""

    client = APIClient()
    client.force_authenticate(test_user)

    # component_1 and component_2 have both the same code but component_3 has different
    component_1 = Component.objects.create(
        code='15016610',
        location=test_location,
        quantity=1000,
        weight=20,
    )
    component_2 = Component.objects.create(
        code='15016610',
        location=test_location,
        quantity=500,
        weight=10,
    )

    component_3 = Component.objects.create(
        code='15016812',
        location=test_location,
        quantity=2000,
        weight=15,
    )

    test_location.refresh_from_db()

    response = client.get(f'/api/inventory/check_location/?location_name={location}')
    assert response.status_code == expected_status

    if expected_status == status.HTTP_200_OK:

        message = response.data['message']

        # List of all components grouped by code in our location, sorted by quantity
        sorted_components = response.data['components']

        assert len(sorted_components) == 2
        assert message == f'All components on location {location}'

        # The first element should be component_3 with code 15016812 because it has more quantity 2000
        # The second element should be connected component_1 and component_2 with the same code 15016610
        first_element, second_element = sorted_components

        assert first_element['code'] == '15016812' and first_element['total_quantity'] == component_3.quantity
        assert second_element['code'] == '15016610' and second_element['total_quantity'] == component_1.quantity + component_2.quantity


def test_CheckLocationView_requires_authentication():
    client = APIClient()
    response = client.get('/api/inventory/check_location/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED