import pytest
from users.models import CustomUser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import status
from rest_framework.test import APIClient


# fixtures
@pytest.fixture
def test_user(db):
    return CustomUser.objects.create_user(
        username="test_username",
        password="test_password",
        first_name="test_first_name",
        last_name="test_last_name",
        role="test_role",
    )

@pytest.fixture
def test_manager(db):
    return CustomUser.objects.create_user(
        username="test_username",
        password="test_password",
        first_name="test_first_name",
        last_name="test_last_name",
        role="manager",
    )

@pytest.fixture
def test_warehouseman(db):
    return CustomUser.objects.create_user(
        username="test_username",
        password="test_password",
        first_name="test_first_name",
        last_name="test_last_name",
        role="warehouseman",
    )






#test for /api/users/token/
@pytest.mark.parametrize(
    'payload, expected_status', [
        #correct credentials
        ({'username': 'test_username', 'password':'test_password'}, status.HTTP_200_OK),
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
        'username': 'test_username',
        'password': 'test_password',
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





#test for /api/create_user/
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
    client = APIClient()
    client.force_authenticate(test_warehouseman)

    response = client.post('/api/users/create/', {}, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN