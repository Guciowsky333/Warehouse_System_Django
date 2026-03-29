import secrets
import string
from inventory.models import Component, Location, ReleasedComponent
from rest_framework.exceptions import NotFound
from inventory.utils import validate_unique_code
from django.db.models import Sum, Count
from django.db import transaction



def change_location(unique_code, location):
    """This function takes component by provided
    unique code and change location to provided one"""


    # We are using transaction and select_for_update() in function validate_unique_code
    # to prevent case when 2 or more users would like to change location of the same unique code
    with transaction.atomic():


        if not unique_code or not location:
            raise ValueError('Unique Code and Location are required.')

        # Validate unique code in utilis.py
        component = validate_unique_code(unique_code)

        location = Location.objects.filter(name=location).first()




        if not location:
            raise NotFound(f'Location {location} not found')

        # checking if location don't exceed max weight of location 800 kg
        if location.total_weight + component.weight > 800 :
            raise ValueError(f'The location {location.name} already weighs'
                             f' {location.total_weight} kg, you can"t add another {component.weight} kg.Max weight of one location is 800 kg ')


        # changing location of the component to a new one
        component.location = location
        component.save()

        return {
            "message":"Changed location successfully",
        }


def release_component(unique_code, department):
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


