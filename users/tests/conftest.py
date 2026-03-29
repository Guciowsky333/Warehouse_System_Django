import pytest
from users.models import CustomUser
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