import pytest

from list_LPT.models import *
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
    """In this test we take  two components with code '15016610' from fixture then we send request to our endpoint
    to check whether it validates code and quantity correctly."""

    client = APIClient()
    client.force_authenticate(test_user_foreman)


    # total quantity of this both components is 2000
    component_15016610_1 = test_components_15016610[0]
    component_15016610_2 = test_components_15016610[1]

    response = client.get(f'/api/list_LPT/validate_component/?code={code}&quantity={quantity}')
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

    # The first one should be component with code 15016610 and 2000 quantity
    assert order_components_in_list[0].code == '15016610'
    assert order_components_in_list[0].quantity == 2000

    # The second one should be component with code 15016812 and 1000 quantity
    assert order_components_in_list[1].code == '15016812'
    assert order_components_in_list[1].quantity == 1000

    # The third one should be component with code 15016808 and 2000 quantity
    assert order_components_in_list[2].code == '15016808'
    assert order_components_in_list[2].quantity == 2000


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


def test_CreateListView_with_warehouseman_role(test_user_warehouseman):
    client = APIClient()
    client.force_authenticate(test_user_warehouseman)
    response = client.get('/api/list_LPT/create_list/')
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_CreateListView_requires_authentication():
    client = APIClient()
    response = client.get('/api/list_LPT/create_list/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED








