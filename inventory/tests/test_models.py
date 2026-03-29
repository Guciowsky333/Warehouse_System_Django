import pytest
from inventory.models import Location, Component
from django.utils import timezone




def test_location_total_weight(test_location_for_models, test_component_for_models, test_component2_for_models):

    # Inside test_location are already 2 components test_component and test_component2
    # so total_weight should return sum weight both of them
    assert test_location_for_models.total_weight == test_component_for_models.weight + test_component2_for_models.weight

def test_component_unique_code(test_component_for_models):

    # checking if unique code was generated correctly and has exactly 15 digits
    assert len(test_component_for_models.unique_code) == 15
