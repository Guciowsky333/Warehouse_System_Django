import pytest
from inventory.models import Location, Component
from django.utils import timezone


@pytest.fixture
def test_location(db):
    return Location.objects.create(name="test_location")


@pytest.fixture
def test_component(db, test_location):
    return Component.objects.create(
        code="test_component",
        location=test_location,
        weight=20,
        quantity=1000,
    )
@pytest.fixture
def test_component2(db, test_location):
    return Component.objects.create(
        code="test_complement",
        location=test_location,
        weight=30,
        quantity=500,
    )

def test_location_total_weight(test_location, test_component, test_component2):

    # Inside test_location are already 2 components test_component and test_component2
    # so total_weight should return sum weight both of them
    assert test_location.total_weight == test_component.weight + test_component2.weight

def test_component_unique_code(test_component):

    # checking if unique code was generated correctly and has exactly 15 digits
    assert len(test_component.unique_code) == 15
