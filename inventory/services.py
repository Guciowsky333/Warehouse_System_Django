import secrets
import string
def generate_unique_code():
    """This function generates a unique code
    with 15 numbers for each component"""

    from inventory.models import Component
    while True:
        unique_code = ''.join(secrets.choice(string.digits) for _ in range(15))

        # checking if component with the same unique code already exist
        if not Component.objects.filter(unique_code=unique_code).exists():
            return unique_code



