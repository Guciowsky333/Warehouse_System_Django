import secrets
import string
from inventory.models import Component, Location, ReleasedComponent
from rest_framework.exceptions import NotFound
from inventory.utils import validate_unique_code
from django.db.models import Sum, Count
from django.db import transaction
from history.models import ComponentHistory



def change_location(unique_code, location_name, user):
    """This function takes component by provided
    unique code and change location to provided one"""


    # We are using transaction and select_for_update() in function validate_unique_code
    # to prevent case when 2 or more users would like to change location of the same unique code
    with transaction.atomic():


        if not unique_code or not location_name:
            raise ValueError('Unique Code and Location are required.')


        # Location EXTC is a special location to accepting components on storge only by manager users
        if location_name == 'EXTC':
            raise ValueError('You can locate component on this location this location is used to '
                             'accepting components on storage from outside')

        # Validate unique code in utilis.py
        component = validate_unique_code(unique_code)

        location = Location.objects.filter(name=location_name).first()

        if not location:
            raise NotFound(f'Location {location_name} not found')

        # checking if location don't exceed max weight of location 800 kg
        if location.total_weight + component.weight > 800:
            raise ValueError(f'The location {location.name} already weighs'
                             f' {location.total_weight} kg, you can"t add another {component.weight} kg.Max weight of one location is 800 kg ')

        # Adding this to history
        ComponentHistory.objects.create(
            action="change_location",

            code=component.code,
            unique_code=component.unique_code,
            quantity=component.quantity,
            weight=component.weight,

            user=user,
            full_name=user.full_name(),

            previous_location= component.location.name,
            current_location= location.name,
        )

        # changing location of the component to a new one
        component.location = location
        component.save()



        return {
            "message":"Changed location successfully",
        }


def release_component(unique_code, department, user):
    """This function takes component from warehouse by unique code
    remove it and create released component model based on data from removing component """


    # We are using transaction and select_for_update() in function validate_unique_code
    # to prevent case when 2 or more users would like to release the same unique code at the same time

    # And also tu ensure that if something goes wrong with 2 operations
    #(delete Component and create ReleasedComponent) none will be done
    with transaction.atomic():

        if not unique_code or not department:
            raise ValueError('Unique Code and Department are required.')

        allow_departments = ['5000','5500','5800','6000']

        department = str(department)
        if department not in allow_departments:
            raise ValueError(f'Department {department} is not exists')

        # Validate unique code in utilis.py
        component = validate_unique_code(unique_code)

        # Creating released component model
        released_component = ReleasedComponent.objects.create(
            code = component.code,
            unique_code = component.unique_code,
            weight = component.weight,
            quantity = component.quantity,
            department = department,
        )

        # Adding this to history
        ComponentHistory.objects.create(
            action="component_release",

            code = component.code,
            unique_code = component.unique_code,
            quantity = component.quantity,
            weight = component.weight,

            user=user,
            full_name = user.full_name(),

            previous_location = component.location.name,
            current_location = department
        )

        # Removing component from warehouse
        component.delete()

        return {
            "message":"Release component successfully",
        }


def check_location(location):
    """This function will show users what components are inside provided location
    and also special fields total_boxes - Amount of  boxes with the same code and
    total_quantity - Sum quantity components with the same code """

    if not location:
        raise ValueError('Location is required.')

    location = Location.objects.filter(name=location).first()
    if not location:
        raise NotFound('Location not found')

    # We are taking all components from provided location
    # then group by code and count total_quantity for each code.Components are order by total_quantity descending
    components = location.components.all().values('code').annotate(
        total_boxes=Count('id'),
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')

    return components





def check_component(code):
    """This function will show users locations of a component that they provided sorted by date.
    This method is called FIFO(First in First Out) and it will show in what order they should release components """

    if not code:
        raise ValueError('Code is required.')

    components = Component.objects.select_related('location').filter(code=code).order_by('production_date')

    if not components.exists():
        raise NotFound(f'Component {code} not found')

    return components




def check_component_grouped(code):
    """This function will show users locations of a component that they provided but this time it will show total
    quantity of components and total boxes with provided code for each location sorted by total quantity. So if we have 3 boxes
    with the same code at the same location function return they as one and total their quantity and boxes"""

    if not code:
        raise ValueError('Code is required.')

    components = Component.objects.filter(code=code).values('location__name').annotate(
        total_boxes=Count('id'),
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')

    if not components.exists():
        raise NotFound(f'Component {code} not found')

    return components


def component_quantity_at_department(code, department):
    """T
    Return total quantity and number of boxes of provided component in provided department
    """

    if not code or not department:
        raise ValueError('Code and Department are required.')

    # checking departments before queryset
    allows_departments = ['5000','5500','5800','6000']
    if department not in allows_departments:
        raise ValueError(f'Department {department} is not exists')



    result = ReleasedComponent.objects.filter(department=department, code=code).values('code').annotate(
        total_boxes=Count('id'),
        total_quantity=Sum('quantity')
    )

    if not result.exists():
        raise NotFound(f'Not founding component {code} in department {department}')

    total_boxes = result[0]['total_boxes']
    total_quantity = result[0]['total_quantity']

    return total_boxes, total_quantity

def component_quantity_at_stock(code):
    """
    Return total quantity and number of boxes of provided component in stock
    """

    if not code:
        raise ValueError('Code is required.')

    result = Component.objects.filter(code=code).values('code').annotate(
        total_boxes=Count('id'),
        total_quantity=Sum('quantity')
    )

    if not result.exists():
        raise NotFound(f'Not founding component {code}')

    total_boxes = result[0]['total_boxes']
    total_quantity = result[0]['total_quantity']

    return total_boxes, total_quantity


def undo_component(unique_code, location_name, user):
    """
    Returns the given component from department back to the warehouse at the specified location.

    This function will remove ReleasedComponent with provided unique code ( if it exists) and
    create again the component model with the same data such as unique code, quantity and weight and
    specified location ( if it exists amd if this location won't exceed 800 kg limit per location
    after adding this component)
    """
    with transaction.atomic():
        if not unique_code or not location_name:
            raise ValueError('Unique Code and Location are required.')


        if location_name == 'EXTC':
            raise ValueError('You can not locate component on location EXTC.'
                             'It is special location for accepting components into the warehouse.')


        location = Location.objects.filter(name=location_name).first()
        if not location:
            raise NotFound('Location not found')

        released_component = ReleasedComponent.objects.select_for_update().filter(unique_code=unique_code).first()
        if not released_component:
            raise NotFound('Component not found')

        if location.total_weight + released_component.weight > 800:
            raise ValueError(f'You can"t add component {released_component.code} to location {location.name}'
                             f'total weight of location can"t exceed 800 kg')

        # Creating component with the same data as our released_component
        Component.objects.create(
            code=released_component.code,
            unique_code=unique_code,
            location=location,
            weight=released_component.weight,
            quantity=released_component.quantity,
        )

        # Adding this to history
        ComponentHistory.objects.create(
            action="component_undo",

            code=released_component.code,
            unique_code=released_component.unique_code,
            quantity=released_component.quantity,
            weight=released_component.weight,

            user=user,
            full_name=user.full_name(),

            previous_location=released_component.department,
            current_location=location.name,
        )

        # Removing our released_component
        released_component.delete()

        return {
            'message':f'Component {unique_code} was successfully returned to stock',
        }


def receiving_the_component_into_the_warehouse(code,weight, quantity):
    """
    Create a component model with EXTC location

    EXTC location is used to receive components into the warehouse.
    So if any component is on EXTC location it means that it has just received at the warehouse
    """

    if not code or not weight or not quantity:
        raise ValueError('Code and Weight and Quantity are required.')

    if not str(quantity).isdigit():
        raise ValueError('Quantity must be a number')

    location_EXTC = Location.objects.filter(name='EXTC').first()


    Component.objects.create(
        code=code,
        weight=weight,
        quantity=quantity,
        location=location_EXTC,
    )

    return {
        'message':f'The {code} component was successfully received into the warehouse',
    }