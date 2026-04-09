from inventory.services import component_quantity_at_stock
from list_LPT.models import *
from rest_framework.exceptions import NotFound
from inventory.models import Component, ReleasedComponent
from users.models import CustomUser
from history.models import ComponentHistory
from django.db.models import Sum
from typing import TypedDict
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

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



    if not str(quantity).isdigit():
        raise ValueError('Quantity must be a number')

    quantity = int(quantity)
    components = Component.objects.filter(list__isnull=True)

    if not components.filter(code=code).exists():
        raise NotFound('Code not found')

    total_quantity_at_stock = components.filter(code=code).aggregate(total_quantity=Sum('quantity'))
    if quantity > total_quantity_at_stock['total_quantity']:
        raise ValueError(f'Dont enough quantity at stock. In the stock is only {total_quantity_at_stock['total_quantity']}')

    return code, quantity





class Item(TypedDict):
    code : str
    quantity : int
def create_list(order_components:list[Item], department:str, user:CustomUser) -> dict:
    """
    This function creates a list to provided department and create OrderComponent model with components
    that user want to order from warehouse if they pass validations and added them to the list.
    The function also assigned all boxes of ordered components (Component model) sorted by FIFO method (First in First out)
    """

    # we use transaction.atomic() to dont create a listLPT when one of the provided components won't pass validations
    with transaction.atomic():

        if not order_components or not department:
            raise ValueError('Fields order_components and department are required')

        list_lpt = ListLPT.objects.create(
            department=department,
            user=user
        )

        for order_component in order_components:
            code = order_component['code']
            quantity = order_component['quantity']

            valid_code, valid_quantity = validate_component(code, quantity)

            if list_lpt.order_components.filter(code=code).exists():
                raise ValueError(f'Code {code} is already on this list you can"t ordered it twice')


            # taking all components with provided code sorted by date (FIFO)
            components = Component.objects.filter(code=valid_code).order_by('production_date')
            total_quantity = 0
            boxes_count = 0

            for component in components:

                # We assign components to our list sorted by date until total quantity of that component
                # will be higher or equal to quantity that user want to order from warehouse
                if total_quantity >= valid_quantity:
                    continue
                boxes_count += 1

                total_quantity += component.quantity
                component.list = list_lpt
                component.save()

            OrderComponent.objects.create(
                list=list_lpt,
                code=valid_code,
                quantity=valid_quantity,
                total_boxes= boxes_count,
            )

    return {
        'message':'List was created successfully',
        'list_number': list_lpt.list_number,
    }


def released_component_from_list(list_number: str, unique_code: str, user:CustomUser) -> dict:
    """
    This function check whether a list with provided number exist and if component with provided unique code exists
    in this list.If yes it removing this component from warehouse and create ReleasedComponent and ComponentHistory
    """

    with transaction.atomic():

        if not list_number or not unique_code:
            raise ValueError('Fields list_number and unique_code are required')

        try:
            list_lpt = ListLPT.objects.get(list_number=list_number)
        except ObjectDoesNotExist:
            raise NotFound(f'List number {list_number} not found')


        if list_lpt.closed:
            raise ValueError('This list has already been closed')


        # First we check if component with provided unique code exist in stock at all
        try:
            component = Component.objects.select_for_update().get(unique_code=unique_code)
        except ObjectDoesNotExist:
            raise NotFound(f'Component {unique_code} not found at stock')


        # Taking all components from our list
        components_in_list = list_lpt.components.all()

        if component not in components_in_list:
            raise ValueError('This component is not on this list')



        # and then add a quantity of this component to filed already_released in OrderComponent model
        # adn to the end removing this component from warehouse

        # We create ReleasedComponent and ComponentHistory with data from our component
        ReleasedComponent.objects.create(
            code= component.code,
            unique_code=component.unique_code,
            weight=component.weight,
            quantity=component.quantity,
            department=list_lpt.department,
        )

        ComponentHistory.objects.create(
            action='component_release',

            code = component.code,
            unique_code = component.unique_code,
            weight = component.weight,
            quantity = component.quantity,

            user = user,
            full_name = user.full_name(),

            previous_location = component.location.name,
            current_location = list_lpt.department,
        )

        order_component = OrderComponent.objects.filter(code=component.code, list=list_lpt).first()

        # We add quantity of this component to filed 'already_released_quantity' in OrderComponent model with this code
        order_component.already_released_quantity += component.quantity

        # And we add 1 box of this component to filed 'already_released_boxes' in OrderComponent model with this code
        order_component.already_released_boxes += 1

        order_component.save()


        component.delete()

        message = 'Component has been released successfully'


        # We check whether filed 'already_released_quantity' in our ComponentOrder is higher or equal to quantity that user want to order.
        # This value can be higher because sometimes we can store components with not regular quantity, but they may be the oldest one.
        # In this case according to FIFO method we assign them to list at first
        # and this is why we sometimes have to released more than is ordered
        if order_component.already_released_quantity >= order_component.quantity:
            order_component.everything_released = True
            order_component.save()

            message = 'You released whole quantity of this component from list'


        # If all OrderComponents in our list have filed 'everything_released' = True it means that
        # user released whole component from list so we closed this list
        if not list_lpt.order_components.filter(everything_released=False).exists():
            list_lpt.closed = True
            list_lpt.save()

            message = 'The list was closed correctly'


        return {
            'message': message,
        }



def validate_list(list_number:str) -> ListLPT:

    if not list_number:
        raise ValueError('Filed list_number are required')

    try:
        list_lpt = ListLPT.objects.get(list_number=list_number)
    except ObjectDoesNotExist:
        raise NotFound(f'List number {list_number} not found')

    return list_lpt












