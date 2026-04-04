import secrets
import string


def generate_number_of_list():

    from list_LPT.models import LPT_list
    numbers = string.digits

    while True:
        # generate random numer of list
        list_number = ''.join(secrets.choice(numbers) for _ in range(10))

        # checking if list of this number already exist
        if not LPT_list.objects.filter(list_number=list_number).exists():
            return list_number

