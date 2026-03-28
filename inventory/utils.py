import secrets
import string

from rest_framework.exceptions import NotFound


def generate_unique_code():
    """This function generates a unique code
    with 15 numbers for each component"""

    from inventory.models import Component, ReleasedComponent


    while True:
        unique_code = ''.join(secrets.choice(string.digits) for _ in range(15))

        # checking if component model or ReleasedComponent model with the same unique code already exist
        if not Component.objects.filter(unique_code=unique_code).exists() and not ReleasedComponent.objects.filter(unique_code=unique_code).exists():
            return unique_code


def validate_unique_code(unique_code):
    """This function validates a unique code
    checking whether provided unique code has been released from warehouse,
    and now it is at the production (if yes return a message with special status "4"
    means that this component has been already released from warehouse).Then checking
    whether component with this unique code exist at the warehouse (if yes return this component)."""

    from inventory.models import Component, ReleasedComponent

    if ReleasedComponent.objects.filter(unique_code=unique_code).exists():
        raise ValueError(f'Status "4" - Component {unique_code} already is in production')

    component = Component.objects.filter(unique_code=unique_code).first()
    if not component:
        raise NotFound(f'Component with unique code {unique_code} not found')

    return component
