import secrets
import string
from inventory.models import Component, Location



def change_location(unique_code, location):


    component = Component.objects.filter(unique_code=unique_code).first()
    location = Location.objects.filter(name=location).first()

    # checking if component with provided unique code exists
    if not component:
        raise ValueError(f'Component with unique code {unique_code} not found')

    # checking if provided location exist at warehouse
    if not location:
        raise ValueError(f'Location {location} not found')

    # checking if location don't exceed max weight of location 800 kg
    if location.total_weight + component.weight > 800 :
        raise ValueError(f'The location {location} already weighs'
                         f' {location.total_weight} kg, you can"t add another {component.weight} kg.Max weight of one location is 800 kg ')

    # changing location of the component to a new one
    component.location = location
    component.save()

    return {
        "message":"Changed location successfully",
    }
