from inventory.services import component_quantity_at_stock
from list_LPT.models import *
from rest_framework.exceptions import NotFound
from inventory.models import Component
from django.db.models import Sum
from typing import TypedDict
from django.db import transaction

def validate_component(code, quantity):
    """
    This function validates a single component and returns its code and quantity.

    Note: function checks only components with list = null because if component already has been assigned
    to some list it can not be added to another list

    It is used to provide real-time feedback to the users they want to create a list with components.
    Note: create_list function also validates components again to prevent case when user would like to
    omit endpoint that check only single component
    """

    if not code or not quantity:
        raise ValueError('Fields code and quantity are required')

    if not quantity.isdigit():
        raise ValueError('Quantity must be an integer')


    components = Component.objecst.filter(list__isnull=True)

    if not components.filter(code=code).exists():
        raise NotFound('Code not found')

    total_quantity_at_stock = components.filter(code=code).aggregate(total_quantity=Sum('quantity'))
    if quantity > total_quantity_at_stock['total_quantity']:
        raise ValueError(f'Dont enough quantity at stock. In the stock is only {component_quantity_at_stock["total_quantity"]}')

    return code, quantity





class Item(TypedDict):
    code : str
    quantity : int
def create_list(order_components:list[Item]) -> str:
    """
    This function creates a list with components that user want to order from warehouse
    (OrderComponent model) if they pass validations.
    THe function also assigned all boxes of ordered components (Component model) sorted by FIFO method (first in first out)
    """

    # we are using transaction.atomic() to dont create a listLPT when one of the provided components won't pass validations
    with transaction.atomic():
        listLPT = ListLPT.objecst.create()

        for order_component in order_components:
            code = order_component['code']
            quantity = order_component['quantity']

            valid_code, valid_quantity = validate_component(code, quantity)

            OrderComponent.objects.create(
                list=listLPT,
                code=valid_code,
                quantity=valid_quantity,
            )

            # taking all components with provided code sorted by date (FIFO)
            components = Component.objects.filter(code=valid_code).order_by('production_date')
            total_quantity = 0

            for component in components:

                # We assign components to our list sorted by date until total quantity of that component
                # will be higher or equal to quantity that user want to order from warehouse
                if total_quantity <= valid_quantity:
                    continue
                total_quantity += component.quantity
                component.list = ListLPT
                component.save()

        return 'List was created successfully'









