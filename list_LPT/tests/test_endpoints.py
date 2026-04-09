import pytest

from inventory.models import *
from list_LPT.models import *
from history.models import *
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.exceptions import NotFound

# test for /api/list_LPT/validate_component/
@pytest.mark.parametrize(
    'code, quantity, expected_status',[
        # Empty code
        ('',2000, status.HTTP_400_BAD_REQUEST),
        # Empty quantity
        ('15016610','',status.HTTP_400_BAD_REQUEST),
        # Quantity that is not a number
        ('15016610','sss',status.HTTP_400_BAD_REQUEST),
        # Code that doesn't exist
        ('wrong_code',2000,status.HTTP_404_NOT_FOUND),
        # User want to order too much quantity of our code we have only 3000 at stock
        ('15016610',3001,status.HTTP_400_BAD_REQUEST),
        # Appropriate data
        ('15016610',2000, status.HTTP_200_OK),

    ]
)
def test_ValidateComponentView(code, quantity, expected_status, test_user_foreman, test_components_15016610):
    """In this test we take 'test_components_15016610' from fixture then we send request to our endpoint
    to check whether it validates code and quantity correctly."""

    client = APIClient()
    client.force_authenticate(test_user_foreman)


    # total quantity at stock is 3000

    body = {
        'code': code,
        'quantity': quantity,
    }

    response = client.post(f'/api/list_LPT/validate_component/', body, format='json')
    assert response.status_code == expected_status

def test_ValidateComponentView_user_with_warehouseman_role(test_user_warehouseman):
    client = APIClient()
    client.force_authenticate(test_user_warehouseman)
    response = client.get('/api/list_LPT/validate_component/')
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_ValidateComponentView_requires_authentication():
    client = APIClient()
    response = client.get('/api/list_LPT/validate_component/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED






# test for /api/list_LPT/create_list/
def test_CreateListView(test_user_foreman, test_components_15016610, test_components_15016812, test_components_15016808):
    """Test creating a list with multiple components and verifying FIFO assignment"""

    client = APIClient()
    client.force_authenticate(test_user_foreman)

    body = {
        'department':'5000',
        'components':[
            {'code':'15016610','quantity':2000},
            {'code':'15016812','quantity':1000},
            {'code':'15016808','quantity':2000},
        ]
    }


    # 3 boxes of 15016610, 1000 each → total 3000
    component_15016610_1, component_15016610_2, component_15016610_3 = test_components_15016610

    # 3 boxes of code 15016812 in the stock the first one has 210 quantity and rest have 500
    # So total quantity of this code will be 1210
    component_15016812_1, component_15016812_2, component_15016812_3 = test_components_15016812

    # 2 boxes of 15016808, 1000 each → total 2000
    component_15016808_1, component_15016808_2 = test_components_15016808

    response = client.post('/api/list_LPT/create_list/', body, format='json')


    # refreshing all components
    for component in test_components_15016610 + test_components_15016812 + test_components_15016808:
        component.refresh_from_db()

    assert response.status_code == status.HTTP_201_CREATED

    assert response.data['message'] == 'List was created successfully'

    # checking if our list was created successfully in the database
    assert ListLPT.objects.filter(list_number=response.data['list_number']).exists()

    # checking whether components form our body was added to list correctly
    created_list = ListLPT.objects.filter(list_number=response.data['list_number']).first()
    order_components_in_list = created_list.order_components.all()
    assert len(order_components_in_list) == 3

    # The first one should be component with code 15016610 and 2000 quantity and 2 boxes
    assert order_components_in_list[0].code == '15016610'
    assert order_components_in_list[0].quantity == 2000
    assert order_components_in_list[0].total_boxes == 2

    # The second one should be component with code 15016812 and 1000 quantity and 3 boxes
    assert order_components_in_list[1].code == '15016812'
    assert order_components_in_list[1].quantity == 1000
    assert order_components_in_list[1].total_boxes == 3

    # The third one should be component with code 15016808 and 2000 quantity
    assert order_components_in_list[2].code == '15016808'
    assert order_components_in_list[2].quantity == 2000
    assert order_components_in_list[2].total_boxes == 2


    # Checking whether boxes was added to list correctly according to FIFO method (First in First out)


    # We ordered 2000 quantity of code 15016610 so we expect that in our
    # list will be two boxes sorted by data of this code each one 1000 quantity
    assert component_15016610_1.list == created_list
    assert component_15016610_2.list == created_list

    # In the stock we have 3 boxes so the most recent should not be in our list (component component_15016610_3)
    assert not component_15016610_3.list == created_list

    # The same with code 15016812 but this time we ordered 1000 quantity of this code, and we have 3 boxes with this code
    # In the stock the first one with 210 quantity (It is the oldest one so it will be added at first into our list)
    # And the rest 1000 quantity so all 3 boxes should be in our list even though it is overall 1210 quantity not 1000
    # But FIFO is more important in this case
    assert component_15016812_1.list == created_list
    assert component_15016812_2.list == created_list
    assert component_15016812_3.list == created_list

    # We ordered 2000 quantity of code 15016808, and we have exactly 2000 in the stock so all 2 boxes should be in our list
    assert component_15016808_1.list == created_list
    assert component_15016808_2.list == created_list



@pytest.mark.parametrize(
    'body, expected_status',[
        # Wrong department
        ({
            'department':'wrong_department',
            'components':[
                {'code':'15016610','quantity':2000},
            ]
        },status.HTTP_400_BAD_REQUEST),
        # User tried order the same code twice
        ({
             'department': '5000',
             'components': [
                 {'code': '15016610', 'quantity': 2000},
                 {'code': '15016610', 'quantity': 1000},

             ]
         }, status.HTTP_400_BAD_REQUEST),
]
)
def test_CreateListView_invalid_data(body, expected_status, test_user_foreman, test_components_15016610):
    client = APIClient()
    client.force_authenticate(test_user_foreman)
    response = client.post('/api/list_LPT/create_list/', body, format='json')
    assert response.status_code == expected_status



def test_CreateListView_with_warehouseman_role(test_user_warehouseman):
    client = APIClient()
    client.force_authenticate(test_user_warehouseman)
    response = client.get('/api/list_LPT/create_list/')
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_CreateListView_requires_authentication():
    client = APIClient()
    response = client.get('/api/list_LPT/create_list/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test for /api/list_LPT/release_component_from_list/
def test_ReleaseComponentFromListView(test_warehouseman, test_list_lpt, test_location):
    """In this test we assigned 1 OrderComponent model to our list and 2 Component model boxes to our list,
    and then we send two request to our endpoint first one with the first component and second with the
    second component, and we check whether our endpoint correctly changes status of OrderComponent and list and
    if it removed components from warehouse to department"""



    client = APIClient()
    client.force_authenticate(test_warehouseman)


    order_component_1 = OrderComponent.objects.create(
        list=test_list_lpt,
        code = '15016610',
        quantity = 2000,
    )

    component_15016610_1 = Component.objects.create(
        code = '15016610',
        quantity = 1000,
        weight = 10,
        location = test_location,
        list = test_list_lpt,
    )

    component_15016610_2 = Component.objects.create(
        code='15016610',
        quantity=1000,
        weight=10,
        location=test_location,
        list=test_list_lpt,
    )

    body1 = {
        'list_number': test_list_lpt.list_number,
        'unique_code': component_15016610_1.unique_code,
    }

    # First request
    response = client.post('/api/list_LPT/release_component_from_list/', body1, format='json')
    test_list_lpt.refresh_from_db()
    order_component_1.refresh_from_db()

    assert response.status_code == status.HTTP_201_CREATED

    # Checking if our component was released correctly from warehouse to department
    assert not Component.objects.filter(unique_code=component_15016610_1.unique_code).exists()
    assert ReleasedComponent.objects.filter(
        unique_code=component_15016610_1.unique_code,
        department=test_list_lpt.department,
    ).exists()

    # Checking if this whole proces has been added correctly to history
    assert ComponentHistory.objects.filter(
        action = 'component_release',
        unique_code=component_15016610_1.unique_code,
        previous_location = component_15016610_1.location.name,
        current_location = test_list_lpt.department
    ).exists()

    # We didn't release whole quantity from list so status list and OrderComponent should be still false
    assert test_list_lpt.closed == False
    assert order_component_1.everything_released == False

    assert order_component_1.already_released_quantity == component_15016610_1.quantity
    assert order_component_1.already_released_boxes == 1

    # The second request
    body2 = {
        'list_number': test_list_lpt.list_number,
        'unique_code': component_15016610_2.unique_code,
    }
    response = client.post('/api/list_LPT/release_component_from_list/', body2, format='json')
    test_list_lpt.refresh_from_db()
    order_component_1.refresh_from_db()

    # Now we expected that our list will be closed because we released whole components from our list
    assert response.status_code == status.HTTP_201_CREATED
    assert not Component.objects.filter(unique_code=component_15016610_2.unique_code).exists()

    assert order_component_1.everything_released == True
    assert test_list_lpt.closed == True
    assert order_component_1.already_released_quantity == component_15016610_1.quantity + component_15016610_2.quantity
    assert order_component_1.already_released_boxes == 2

@pytest.mark.parametrize(
    'list_number, unique_code, expected_message, expected_status',[
        # User provided list that has been already closed
        ('closed_list', 'test_unique_code', 'This list has already been closed', status.HTTP_400_BAD_REQUEST ),
        # User provided not exist list
        ('wrong_list', 'test_unique_code', 'List number wrong_list not found', status.HTTP_404_NOT_FOUND ),
        # User provided not exist component
        ('test_number', 'wrong_unique_code', 'Component wrong_unique_code not found at stock', status.HTTP_404_NOT_FOUND ),
        # User provided component that is not at the list
        ('test_number', 'test_unique_code1', 'This component is not on this list', status.HTTP_400_BAD_REQUEST ),

    ]

)
def test_ReleaseComponentFromListView_invalid_data(list_number, unique_code, expected_message, expected_status, test_warehouseman,
                                                   test_list_lpt, test_list_lpt_closed, test_component_on_list, test_component_off_list):

    client = APIClient()
    client.force_authenticate(test_warehouseman)

    body = {
        'list_number': list_number,
        'unique_code': unique_code,
    }
    response = client.post('/api/list_LPT/release_component_from_list/', body, format='json')

    assert response.status_code == expected_status
    assert response.data['message'] == expected_message


def test_ReleaseComponentFromListView_requires_authentication():
    client = APIClient()
    response = client.post('/api/list_LPT/release_component_from_list/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED






# Test for /api/list_LPT/list_detail/

@pytest.mark.parametrize(
    'list_number, expected_status',[

        # Not exist list
        ('wrong_number', status.HTTP_404_NOT_FOUND),
        # Appropriate data
        ('test_number', status.HTTP_200_OK),
    ]
)


def test_ListLPTDetailView(list_number, expected_status, test_warehouseman, test_list_lpt):
    """In this test we assigned two OrderComponent models to our list and check whether endpoint
    correctly show us details about our list """

    client = APIClient()
    client.force_authenticate(test_warehouseman)

    order_component_1 = OrderComponent.objects.create(
        list = test_list_lpt,
        code = '15016610',
        quantity = 5000,
        total_boxes = 5,
        already_released_boxes = 3,
        already_released_quantity = 3000,

    )

    order_component_2 = OrderComponent.objects.create(
        list=test_list_lpt,
        code='15016808',
        quantity=3000,
        total_boxes=3,
        already_released_boxes=3,
        already_released_quantity=3000,
        everything_released=True,
    )


    response = client.get(f'/api/list_LPT/list/{list_number}/details/')

    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        data = response.json()
        assert data['user'] == test_list_lpt.user.full_name()
        assert data['department'] == test_list_lpt.department
        assert data['closed'] == test_list_lpt.closed
        assert data['total_boxes_in_list'] == order_component_1.total_boxes + order_component_2.total_boxes
        assert data['total_boxes_in_list_released'] == order_component_1.already_released_boxes + order_component_2.already_released_boxes

        # We now that first element in 'order_components' filed in this list will be order_component_1 and the second will be
        # order_component_2 because they are sorted by quantity in serializer.py
        assert data['order_components'][0]['code'] == order_component_1.code
        assert data['order_components'][0]['quantity'] == order_component_1.quantity
        assert data['order_components'][0]['already_released_quantity'] == order_component_1.already_released_quantity
        assert data['order_components'][0]['total_boxes'] == order_component_1.total_boxes
        assert data['order_components'][0]['already_released_boxes'] == order_component_1.already_released_boxes
        assert data['order_components'][0]['everything_released'] == order_component_1.everything_released

        assert data['order_components'][1]['code'] == order_component_2.code
        assert data['order_components'][1]['quantity'] == order_component_2.quantity
        assert data['order_components'][1]['already_released_quantity'] == order_component_2.already_released_quantity
        assert data['order_components'][1]['total_boxes'] == order_component_2.total_boxes
        assert data['order_components'][1]['already_released_boxes'] == order_component_2.already_released_boxes
        assert data['order_components'][1]['everything_released'] == order_component_2.everything_released


def test_ListLPTDetailView_requires_authentication(test_list_lpt):
    client = APIClient()
    response = client.get(f'/api/list_LPT/list/{test_list_lpt.list_number}/details/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED




