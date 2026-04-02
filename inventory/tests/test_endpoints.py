from platform import android_ver

import pytest
from inventory.models import Location, Component, ReleasedComponent
from inventory.tests.test_models import test_component_unique_code
from users.models import CustomUser
from rest_framework import status
from rest_framework.test import APIClient
from datetime import date
from history.models import ComponentHistory

# test for /api/inventory/change_location/
@pytest.mark.parametrize(
    'payload, expected_status', [

        # User provided empty unique_code
        ({'unique_code':'', 'location':'test_location2'}, status.HTTP_400_BAD_REQUEST),
        # User provided empty location
        ({'unique_code':'test_unique_code', 'location':''}, status.HTTP_400_BAD_REQUEST),
        # User provided unique code that dont exist
        ({'unique_code':'wrong_unique_code', 'location':'test_location2'}, status.HTTP_404_NOT_FOUND),
        # User provided location that dont exist
        ({'unique_code':'test_unique_code', 'location':'wrong_location'}, status.HTTP_404_NOT_FOUND),
        # Status "4" means - User provided unique code that has been already released to production
        ({'unique_code':'test_released_unique_code', 'location':'test_location2'}, status.HTTP_400_BAD_REQUEST),
        # Appropriate data
        ({'unique_code':'test_unique_code', 'location':'test_location2'}, status.HTTP_200_OK),
    ]
)

def test_ChangeLocationView(payload, expected_status, test_component,test_location, test_location2, test_user, test_released_component):
    client = APIClient()
    client.force_authenticate(test_user)

    response = client.patch('/api/inventory/change_location/', payload, format='json')

    assert response.status_code == expected_status


    # checking if our test component has been added to our test location correctly
    if expected_status == status.HTTP_200_OK:
        assert test_location2.components.filter(unique_code="test_unique_code").exists()


        # checking if this action was added correctly in our history
        assert ComponentHistory.objects.filter(
            action = 'change_location',

            code=test_component.code,
            unique_code=test_component.unique_code,
            quantity=test_component.quantity,
            weight=test_component.weight,

            user=test_user,
            full_name=test_user.full_name(),

            previous_location=test_location,
            current_location=test_location2,
        ).exists()

def test_ChangeLocationView_requires_authentication():
    client = APIClient()
    response = client.get('/api/inventory/change_location/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_ChangeLocationView_max_weight(test_location2, test_component, test_user):
    """In this test we assigned to our test location component that weighs 790 kg
    so now we shouldn't be albe to add our test component that weighs 20 kg to this location
    because each location can't exceed 800 kg"""


    client = APIClient()
    client.force_authenticate(test_user)



    Component.objects.create(
        code="heavy_component",
        unique_code="heavy_unique_code",
        location=test_location2,
        weight=790,
        quantity=1000,
    )

    test_location2.refresh_from_db()

    body = {
        'unique_code': 'test_unique_code',
        'location': 'test_location2'
    }

    response = client.patch('/api/inventory/change_location/', body, format='json')


    assert response.status_code == status.HTTP_400_BAD_REQUEST


    # Checking if the total_weight of our location is still 790 kg
    assert test_location2.total_weight == 790

    # Checking whether the test component not has been added to our test location as we expected
    assert not test_location2.components.filter(unique_code='test_unique_code').exists()





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

    component = test_component


    response = client.post('/api/inventory/release_component/', payload, format='json')
    assert response.status_code == expected_status

    if expected_status == status.HTTP_201_CREATED:

        # Checking if our component has been removed from warehouse
        assert not Component.objects.filter(unique_code=payload['unique_code']).exists()

        # Checking if model ReleasedComponent with the same unique code and provided department has been created correctly
        assert ReleasedComponent.objects.filter(unique_code=payload['unique_code'], department=payload['department']).exists()

        assert response.data['message'] == 'Release component successfully'

        # checking if this action was added correctly in our history
        assert ComponentHistory.objects.filter(
            action='component_release',

            code=test_component.code,
            unique_code=test_component.unique_code,
            quantity=test_component.quantity,
            weight=test_component.weight,

            user=test_user,
            full_name=test_user.full_name(),

            previous_location=test_component.location.name,
            current_location=payload['department'],
        ).exists()




def test_ReleasedComponentView_requires_authentication():
    client = APIClient()
    response = client.get('/api/inventory/release_component/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Tests for /api/inventory/check_location/
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
    So the endpoint should return 2 components, the first and second as one and the third with different code,
    Each component is a 1 box so if we have two components with the same code endpoint also should return total_boxes of that code as 2
    """

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

        # The first element should be component_3 with code 15016812 because it has more quantity than second element
        # The first element also should contain total_boxes as 1 because we assigned only one component with code 15016812 to our location

        # The second element should be connected component_1 and component_2 with the same code 15016610
        # The second element should contain total_boxes as 2 because we assigned 2 components with the same code 15016610 to our location
        first_element, second_element = sorted_components


        assert first_element['code'] == '15016812' and first_element['total_quantity'] == component_3.quantity
        assert first_element['total_boxes'] == 1

        assert second_element['code'] == '15016610' and second_element['total_quantity'] == component_1.quantity + component_2.quantity
        assert second_element['total_boxes'] == 2


def test_CheckLocationView_requires_authentication():
    client = APIClient()
    response = client.get('/api/inventory/check_location/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED




# Tests for /api/inventory/check_component/
@pytest.mark.parametrize(
    'code, expected_status', [
        # Empty code
        ('', status.HTTP_400_BAD_REQUEST),
        # User provided code that dont exist
        ('wrong_code', status.HTTP_404_NOT_FOUND),
        # Appropriate data
        ('15016812', status.HTTP_200_OK),
    ]
)

def test_CheckComponentView(code, expected_status,test_location,test_location2, test_user):
    """First we are creating 2 components with the same test code '15016812' and assigned them to different locations.
    So, after we provide our test code the endpoint should return 2 components along with information
    such as locations or quantities of that components order by date (FIFO)"""

    client = APIClient()
    client.force_authenticate(test_user)

    older_component = Component.objects.create(
        code='15016812',
        unique_code='older_component_unique_code',
        location=test_location,
        quantity=1000,
        weight=20,
    )

    younger_component = Component.objects.create(
        code='15016812',
        unique_code='younger_component_unique_code',
        location=test_location2,
        quantity=500,
        weight=10,
    )

    # Now we overwrite date of that two components the first one will be older and the second will be younger
    # So the older component should be first in endpoint response according to FIFO (first in first out)
    older_component.production_date = date(2020, 1, 1)


    younger_component.production_date = date(2021, 1, 1)

    response = client.get(f'/api/inventory/check_component/?code={code}')

    assert response.status_code == expected_status

    if expected_status == status.HTTP_200_OK:
        assert response.data['message'] == f'All locations for component {code}'
        assert len(response.data['components']) == 2

        component_1, component_2 = response.data['components']

        # We expect that first component will be the older one
        assert component_1['unique_code'] == 'older_component_unique_code'
        assert component_1['location_name'] == test_location.name

        # And the second one will be younger
        assert component_2['unique_code'] == 'younger_component_unique_code'
        assert component_2['location_name'] == test_location2.name

def test_CheckComponentView_requires_authentication():
    client = APIClient()
    response = client.get('/api/inventory/check_component/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# # Tests for /api/inventory/check_component/grouped/
@pytest.mark.parametrize(
    'code, expected_status', [
        # Empty code
        ('', status.HTTP_400_BAD_REQUEST),
        # Not exist code
        ('wrong_code', status.HTTP_404_NOT_FOUND),
        # Appropriate data
        ('15016610', status.HTTP_200_OK),
    ]
)

def test_CheckComponentGroupedView(code, expected_status,test_location,test_location2, test_user):
    """In this test we are creating 3 components with the same code '15016610' both of them to the same location
    'test_location' and the last one to a different location 'test_location2'. We expect that endpoint returns two
    element sorted by total quantity the first one will be grouped 2 components with the same
    location and sum their quantities and amount of boxes and the second one will be single component at the different location """

    client = APIClient()
    client.force_authenticate(test_user)

    component_1 = Component.objects.create(
        code='15016610',
        location=test_location,
        quantity=1000,
        weight=20,
    )

    component_2 = Component.objects.create(
        code='15016610',
        location=test_location,
        quantity=1000,
        weight=20,
    )

    # different location
    component_3 = Component.objects.create(
        code='15016610',
        location=test_location2,
        quantity=1000,
        weight=20,
    )

    response = client.get(f'/api/inventory/check_component/grouped/?code={code}')

    assert response.status_code == expected_status

    if expected_status == status.HTTP_200_OK:
        assert response.data['message'] == f'All locations for component {code}'
        assert len(response.data['components']) == 2

        first_element, second_element = response.data['components']

        # We expect that first element will be component_1 and component_2 as one
        # because they have bigger total quantity that second element
        assert first_element['location__name'] == test_location.name
        assert first_element['total_boxes'] == 2
        assert first_element['total_quantity'] == component_1.quantity + component_2.quantity

        # We expect that second element will be singe component_3 because it has less total quantity
        assert second_element['location__name'] == test_location2.name
        assert second_element['total_boxes'] == 1
        assert second_element['total_quantity'] == component_3.quantity

def test_CheckComponentGroupedView_requires_authentication():
    client = APIClient()
    response = client.get('/api/inventory/check_component/grouped/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test api/inventory/quantity_in_department/

@pytest.mark.parametrize(
    'code, department, expected_status', [
        ('', '5000', status.HTTP_400_BAD_REQUEST),
        ('15016808', '', status.HTTP_400_BAD_REQUEST),
        ('wrong_code', '5000', status.HTTP_404_NOT_FOUND),
        ('15016610', 'wrong_department', status.HTTP_404_NOT_FOUND),
        ('15016808', '5000', status.HTTP_200_OK),
    ]
)

def test_ShowQuantityInDepartmentView(code, department, expected_status,test_user):
    """In this test we are creating 2 ReleasedComponent with the same code '15016808' and the same department
    '5000' and we expect that endpoint returns us sum quantity and boxes of code '15016808' in our department """

    client = APIClient()
    client.force_authenticate(test_user)

    released_component1 = ReleasedComponent.objects.create(
        code='15016808',
        unique_code='unique_code',
        department='5000',
        quantity=1000,
        weight=20,
    )

    released_component2 = ReleasedComponent.objects.create(
        code='15016808',
        unique_code='unique_code1',
        department='5000',
        quantity=500,
        weight=10,
    )

    response = client.get(f'/api/inventory/quantity_in_department/?code={code}&department={department}')

    assert response.status_code == expected_status

    if expected_status == status.HTTP_200_OK:
        assert response.data['code'] == f'{code}'
        assert response.data['department'] == f'{department}'
        assert response.data['total_quantity'] == released_component1.quantity + released_component2.quantity
        assert response.data['total_boxes'] == 2


def test_ShowQuantityInDepartmentView_requires_authentication(test_user):
    client = APIClient()
    response = client.get('/api/inventory/quantity_in_department/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# # Test api/inventory/quantity_in_stock/
@pytest.mark.parametrize(
    'code, expected_status', [
        ('', status.HTTP_400_BAD_REQUEST),
        ('wrong_code', status.HTTP_404_NOT_FOUND),
        ('15016807', status.HTTP_200_OK),
    ]
)
def test_ShowQuantityInStockView(code, expected_status, test_user, test_location):
    """In this test we are creating 2 Components with the same code '15016807'.
    We expect that endpoint returns us total quantity of a component with provided code  and number of boxes in stock"""

    client = APIClient()
    client.force_authenticate(test_user)

    component_1 = Component.objects.create(
        code='15016807',
        location=test_location,
        quantity=1000,
        weight=20,
    )

    component_2 = Component.objects.create(
        code='15016807',
        location=test_location,
        quantity=500,
        weight=20,
    )

    response = client.get(f'/api/inventory/quantity_in_stock/?code={code}')

    assert response.status_code == expected_status

    if expected_status == status.HTTP_200_OK:
        assert response.data['code'] == f'{code}'
        assert response.data['total_quantity'] == component_1.quantity + component_2.quantity
        assert response.data['total_boxes'] == 2

def test_ShowQuantityInStockView_requires_authentication(test_user):
    client = APIClient()
    response = client.get('/api/inventory/quantity_in_stock/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# Test for api/inventory/undo_component/
@pytest.mark.parametrize(
    'payload, expected_status', [
        # Empty unique_code
        ({'unique_code':'','location':'test_location'}, status.HTTP_400_BAD_REQUEST),
        # Empty location
        ({'unique_code':'test_released_unique_code','location':''}, status.HTTP_400_BAD_REQUEST),
        # not exist unique_code
        ({'unique_code':'wrong_unique_code','location':'test_location'}, status.HTTP_404_NOT_FOUND),
        # not exist location
        ({'unique_code':'test_released_unique_code','location':'wrong_location'}, status.HTTP_404_NOT_FOUND),
        # Appropriate data
        ({'unique_code':'test_released_unique_code','location':'test_location'}, status.HTTP_201_CREATED),
    ]
)

def test_UndoComponentView(payload, expected_status, test_user, test_released_component, test_location):
    """This test checking if ReleasedComponent with provided unique code was removed correctly and if new
     Component with the same data as ReleasedComponent and provided location was created successfully """

    client = APIClient()
    client.force_authenticate(test_user)


    response = client.post('/api/inventory/undo_component/', payload, format='json')

    assert response.status_code == expected_status

    if expected_status == status.HTTP_201_CREATED:
        assert not ReleasedComponent.objects.filter(unique_code='test_released_unique_code').exists()


        component = Component.objects.get(unique_code='test_released_unique_code')
        assert component.code == test_released_component.code
        assert component.unique_code == test_released_component.unique_code
        assert component.weight == test_released_component.weight
        assert component.quantity == test_released_component.quantity
        assert component.location == test_location


        # checking if this action was added correctly in our history
        assert ComponentHistory.objects.filter(
            action='component_undo',

            code=test_released_component.code,
            unique_code=test_released_component.unique_code,
            quantity=test_released_component.quantity,
            weight=test_released_component.weight,

            user=test_user,
            full_name=test_user.full_name(),

            previous_location=test_released_component.department,
            current_location=test_location.name,
        ).exists()



def test_UndoComponentView_max_weight(test_user, test_location, test_released_component):

    client = APIClient()
    client.force_authenticate(test_user)

    Component.objects.create(
        code='heavy_component',
        unique_code='unique_code',
        location=test_location,
        weight=790,
        quantity=1000,
    )

    body = {
        'unique_code': test_released_component.unique_code,
        'location': test_location.name,
    }

    response = client.post('/api/inventory/undo_component/', body, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['message'] == (f'You can"t add component {test_released_component.code} to location {test_location.name}'
                             f'total weight of location can"t exceed 800 kg')

    assert test_location.total_weight == 790
    assert not test_location.components.filter(unique_code=test_released_component.unique_code).exists()


def test_UndoComponentView_requires_authentication(test_user):
    client = APIClient()
    response = client.get('/api/inventory/undo_component/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test for api/inventory/receive_component/
@pytest.mark.parametrize(
    'payload, expected_status', [
        # Empty code
        ({'code':'','weight':20,'quantity':1000},status.HTTP_400_BAD_REQUEST),
        # Empty weight
        ({'code':'15016610','weight':'','quantity':1000},status.HTTP_400_BAD_REQUEST),
        # Empty quantity
        ({'code':'15016610','weight':20,'quantity':''},status.HTTP_400_BAD_REQUEST),
        # Appropriate data
        ({'code':'15016610','weight':20,'quantity':1000},status.HTTP_201_CREATED),

    ]
)

def test_ReceivingComponentView(payload, expected_status, test_manager, test_location_EXTC):

    client = APIClient()
    client.force_authenticate(test_manager)

    response = client.post('/api/inventory/receive_component/', payload, format='json')

    assert response.status_code == expected_status

    if expected_status == status.HTTP_201_CREATED:

        assert Component.objects.filter(
            code=payload['code'],
            quantity=payload['quantity'],
            weight=payload['weight'],
            location=test_location_EXTC,
        ).exists()


def test_ReceivingComponentView_not_manager_user(test_user):
    client = APIClient()
    client.force_authenticate(test_user)
    response = client.get('/api/inventory/receive_component/')
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_ReceivingComponentView_requires_authentication(test_manager):
    client = APIClient()
    response = client.get('/api/inventory/receive_component/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED