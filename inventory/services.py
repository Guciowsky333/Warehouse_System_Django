import secrets
import string
from inventory.models import Component, Location
from rest_framework.exceptions import NotFound



def change_location(unique_code, location):

    # checking if user provided unique_code and location
    if not unique_code or not location:
        raise ValueError('Unique Code and Location are required.')


    component = Component.objects.filter(unique_code=unique_code).first()
    location = Location.objects.filter(name=location).first()

    # checking if component with provided unique code exists
    if not component:
        raise NotFound(f'Component with unique code {unique_code} not found')

    # checking if provided location exist at warehouse
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
