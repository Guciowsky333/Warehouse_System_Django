from urllib import response

import pytest
from rest_framework import status
from rest_framework.test import APIClient


from history.models import *


# Test for api/history/by_code/
@pytest.mark.parametrize(
    'query_params', [
        ('?code=code'),
        ('?unique_code=unique_code'),
        ('?user_name=test user')
    ],
)

def test_history_without_action(query_params, test_user, test_location,test_location2, test_component):
    """
    We create 3 ComponentHistory with our component, first we change it location,
    then released it from warehouse to production, and finally we return it back to then warehouse and then check whether
    endpoint will show us whole history of this component when we provided code of that component
    """

    change_location = ComponentHistory.objects.create(
        action = 'change_location',
        code = test_component.code,
        unique_code = test_component.unique_code,
        weight = test_component.weight,
        quantity = test_component.quantity,
        user = test_user,
        full_name = test_user.full_name(),
        previous_location = test_location2.name,
        current_location = test_location.name
    )

    released_component = ComponentHistory.objects.create(
        action='component_release',
        code=test_component.code,
        unique_code=test_component.unique_code,
        weight=test_component.weight,
        quantity=test_component.quantity,
        user=test_user,
        full_name=test_user.full_name(),
        previous_location=test_location.name,
        current_location='5500'
    )

    undo_component = ComponentHistory.objects.create(
        action='component_undo',
        code=test_component.code,
        unique_code=test_component.unique_code,
        weight=test_component.weight,
        quantity=test_component.quantity,
        user=test_user,
        full_name=test_user.full_name(),
        previous_location='5500',
        current_location=test_location.name,
    )

    client = APIClient()
    client.force_authenticate(user=test_user)

    response = client.get(f'/api/history/{query_params}&action=')

    assert response.status_code == status.HTTP_200_OK

    # The order should be sorted by the mose recent date so it should look lik this :
    # 1.undo_component - 2.released_component - 3.change_location
    first_element, second_element, third_element = response.data['history']
    assert first_element['action'] == undo_component.action
    assert second_element['action'] == released_component.action
    assert third_element['action'] == change_location.action



@pytest.mark.parametrize(
    'action', [
        ('change_location'),
        ('component_release'),
        ('component_undo'),

    ],
)
def test_history_with_action(action, test_user, test_location, test_location2, test_component):
    """
    In this test we create 3 ComponentHistory each one with different action, and we check whether
    our endpoint will correctly return to us only ComponentHistory with action that we provided in query_params
    """

    change_location = ComponentHistory.objects.create(
        action='change_location',
        code=test_component.code,
        unique_code=test_component.unique_code,
        weight=test_component.weight,
        quantity=test_component.quantity,
        user=test_user,
        full_name=test_user.full_name(),
        previous_location=test_location2.name,
        current_location=test_location.name
    )

    released_component = ComponentHistory.objects.create(
        action='component_release',
        code=test_component.code,
        unique_code=test_component.unique_code,
        weight=test_component.weight,
        quantity=test_component.quantity,
        user=test_user,
        full_name=test_user.full_name(),
        previous_location=test_location.name,
        current_location='5500'
    )

    undo_component = ComponentHistory.objects.create(
        action='component_undo',
        code=test_component.code,
        unique_code=test_component.unique_code,
        weight=test_component.weight,
        quantity=test_component.quantity,
        user=test_user,
        full_name=test_user.full_name(),
        previous_location='5500',
        current_location=test_location.name,
    )

    client = APIClient()
    client.force_authenticate(user=test_user)

    response = client.get(f'/api/history/?code={test_component.code}&action={action}')

    assert response.status_code == status.HTTP_200_OK


    # In each case our history should storage only one model ComponentHistory with provided action
    assert len(response.data['history']) == 1
    if action == 'change_location':
        result = response.data['history'][0]
        assert result['action'] == change_location.action

    if action == 'component_release':
        result = response.data['history'][0]
        assert result['action'] == released_component.action

    if action == 'component_undo':
        result = response.data['history'][0]
        assert result['action'] == undo_component.action

@pytest.mark.parametrize(
    'code, action, expected_status',[
        # Empty code,
        ('','change_location',status.HTTP_400_BAD_REQUEST),
        # Code that doesnt exist
        ('wrong_code', 'change_location',status.HTTP_404_NOT_FOUND),
        # Wrong action
        ('code', 'wrong_action',status.HTTP_404_NOT_FOUND),

    ]
)
def test_history_with_invalid_data(code, action,expected_status, test_user, test_location,test_location2, test_component):
    """In this test we check whole possible invalid data such as wrong action or wrong code amd more"""


    change_location = ComponentHistory.objects.create(
        action='change_location',
        code=test_component.code,
        unique_code=test_component.unique_code,
        weight=test_component.weight,
        quantity=test_component.quantity,
        user=test_user,
        full_name=test_user.full_name(),
        previous_location=test_location2.name,
        current_location=test_location.name
    )

    client = APIClient()
    client.force_authenticate(user=test_user)
    response = client.get(f'/api/history/?code={code}&action={action}')
    assert response.status_code == expected_status
