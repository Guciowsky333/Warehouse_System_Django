from users.models import CustomUser
import string
import secrets

def generate_username(first_name:str, last_name:str) -> str:
    """Generates username in format:
     first letter of first name + last name + 2 random digits"""

    random_numbers = ''.join(secrets.choice(string.digits) for _ in range(2))
    return f'{first_name[0]}.{last_name}{random_numbers}'

def generate_password() ->str:
    """Generates a random password with 8 lowers characters and 2 numbers on the end"""

    characters = string.ascii_letters.lower()
    numbers = string.digits

    password = ''.join(secrets.choice(characters) for _ in range(8)) + ''.join(secrets.choice(numbers) for _ in range(2))
    return password


def create_CustomUser(validated_data:dict) -> dict:
    """ This function take a validated data from serializer and generate
    username and password for the user and then create a CustomUser object with this data.
    Returns the username and the password in response only one time """

    # taking data from serializer
    first_name = validated_data['first_name']
    last_name = validated_data['last_name']
    role = validated_data['role']

    # generate username and password
    username = generate_username(first_name, last_name)
    password = generate_password()

    # create a CustomUser
    user = CustomUser.objects.create_user(
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=role
    )

    return {
        "message":"User created successfully",
        "username": username,
        "password": password,
    }





