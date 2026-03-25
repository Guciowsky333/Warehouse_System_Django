import pytest
from users.models import CustomUser
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import status
from rest_framework.test import APIClient



@pytest.fixture
def test_user(db):
    return CustomUser.objects.create_user(
        username="test_username",
        password="test_password",
        first_name="test_first_name",
        last_name="test_last_name",
        role="test_role",
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