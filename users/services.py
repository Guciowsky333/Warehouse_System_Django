from rest_framework.exceptions import NotFound

from users.models import CustomUser
from users.utils import generate_password, generate_username


def create_custom_user(first_name: str, last_name: str, role: str) -> dict[str, str]:
    """This function take a validated data from serializer and generate
    username and password for the user and then create a CustomUser object with this data.
    Returns the username and the password in response only one time"""

    # generate username and password
    username = generate_username(first_name, last_name)
    password = generate_password()

    # create a CustomUser
    CustomUser.objects.create_user(
        username=username, password=password, first_name=first_name, last_name=last_name, role=role
    )

    return {
        "username": username,
        "password": password,
    }


def reset_password(username: str) -> dict[str, str]:
    """This function take a username and check if he exists and
    then change his password to a new and return it."""

    user = CustomUser.objects.filter(username=username).first()

    # check if the user exists
    if not user:
        raise NotFound("User not found")

    # generating and set up new password
    new_password = generate_password()
    user.set_password(new_password)
    user.save()

    return {
        "username": user.username,
        "new_password": new_password,
    }
