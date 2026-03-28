import pytest
from users.models import CustomUser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
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
def test_manager(db):
    return CustomUser.objects.create_user(
        username="test_username2",
        password="test_password2",
        first_name="test_first_name2",
        last_name="test_last_name2",
        role="manager",
    )

@pytest.fixture
def test_warehouseman(db):
    return CustomUser.objects.create_user(
        username="test_username3",
        password="test_password3",
        first_name="test_first_name3",
        last_name="test_last_name3",
        role="warehouseman",
    )






#test for /api/users/token/
@pytest.mark.parametrize(
    'payload, expected_status', [
        #correct credentials
        ({'username': 'test_username1', 'password':'test_password1'}, status.HTTP_200_OK),
        #incorrect credentials
        ({'username': 'wrong_username', 'password':'wrong_password'}, status.HTTP_401_UNAUTHORIZED),
    ]
)


def test_obtain_token(payload, expected_status, test_user):
    client = APIClient()
    response = client.post('/api/users/token/', payload, format='json')
    assert response.status_code == expected_status

    if expected_status == status.HTTP_200_OK:
        assert "access" in response.data




#test for /api/users/token/refresh/
def test_refresh_token_with_valid_token(test_user):
    client = APIClient()
    body = {
        'username': 'test_username1',
        'password': 'test_password1',
    }

    #first we obtain refresh token on /api/users/token/ and then check if it works correctly
    response_1 = client.post('/api/users/token/', body, format='json')
    refresh_token = response_1.data['refresh']

    #now we send request with refresh token
    response = client.post('/api/users/token/refresh/', {'refresh': refresh_token}, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data



def test_refresh_token_with_invalid_token():
    client = APIClient()
    response = client.post('/api/users/token/refresh/', {'refresh': 'invalid_token'}, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED





#test for /api/users/create/
@pytest.mark.parametrize(
    'first_name, last_name, role, expected_status', [

        # empty first name
        ('', 'TestLastName', 'manager', status.HTTP_400_BAD_REQUEST),

        # empty last name
        ('TestFirstName', '', 'warehouseman', status.HTTP_400_BAD_REQUEST),

        # user provided first name that contain not only letters
        ('Wrong_name', 'lastname', 'manager', status.HTTP_400_BAD_REQUEST),

        # user provided not existing role
        ('FirstName', 'LastName', 'WrongRole', status.HTTP_400_BAD_REQUEST),

        # everything is correct
        ('name', 'lastname', 'warehouseman', status.HTTP_201_CREATED),

    ]
)

def test_CreateCustomUserView(first_name, last_name, role, expected_status, test_manager):
    client = APIClient()
    client.force_authenticate(test_manager)

    body = {
        'first_name': first_name,
        'last_name': last_name,
        'role': role,
    }
    response = client.post('/api/users/create/', body, format='json')
    assert response.status_code == expected_status

    if expected_status == status.HTTP_201_CREATED:
        assert 'password' in response.data
        assert 'username' in response.data
        assert response.data['message'] == "User created successfully"



def test_create_user_requires_authentication():
    client = APIClient()
    response = client.post('/api/users/create/', {}, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_user_by_not_manager(test_warehouseman):
    """ Checking if the permission IsManager work correctly and block access
        user who is not a manager"""

    client = APIClient()
    client.force_authenticate(test_warehouseman)

    response = client.post('/api/users/create/', {}, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN




#test for /api/reset_password/
@pytest.mark.parametrize(
    'username, expected_message, expected_status', [
        # exist user
        ('test_username3','Password reset successfully', status.HTTP_200_OK),

        # not exist user
        ('wrong_username','User not found', status.HTTP_404_NOT_FOUND)
    ]
)

def test_ResetPasswordView(username,expected_message, expected_status, test_manager, test_warehouseman):
    client = APIClient()
    client.force_authenticate(test_manager)

    response = client.patch('/api/users/reset_password/', {'username': username}, format='json')

    assert response.status_code == expected_status
    assert response.data['message'] == expected_message


    # checking if user's password was changed into a new one
    if expected_status == status.HTTP_200_OK:
        test_warehouseman.refresh_from_db()
        new_password = response.data['new_password']
        assert test_warehouseman.check_password(new_password) is True

def test_reset_password_requires_authentication():
    client = APIClient()
    response = client.patch('/api/users/reset_password/', {}, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED



def test_reset_password_by_not_manager(test_warehouseman):
    """ Checking if the permission IsManager work correctly and block access
        user who is not a manager"""

    client = APIClient()
    client.force_authenticate(test_warehouseman)
    response = client.patch('/api/users/reset_password/', {}, format='json')

    assert response.status_code == status.HTTP_403_FORBIDDEN