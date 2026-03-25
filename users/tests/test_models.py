import pytest
from users.models import CustomUser

@pytest.mark.django_db
def test_CustomUser():
    user = CustomUser.objects.create_user(
        username="test_login",
        password="test_password",
        first_name="test_first_name",
        last_name="test_last_name",
        role="test_role",
    )

    assert user.username == "test_login"
    assert user.check_password('test_password')
    assert user.first_name == "test_first_name"
    assert user.last_name == "test_last_name"
    assert user.role == "test_role"

