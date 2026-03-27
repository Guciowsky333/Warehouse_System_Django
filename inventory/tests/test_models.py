import pytest
from inventory.models import Location, Component
from django.utils import timezone


@pytest.fixture
def test_location(db):
    return Location.objects.create(name="test_location")


@pytest.fixture
def test_component(db, test_location):
    return Component.objects.create(
        code="test_code",
        location=test_location,
        weight=20,
        quantity=1000,
    )



def test_model_location(test_location):
    assert Location.objects.filter(name=test_location.name).exists()


def test_model_component(test_component):
    assert Component.objects.filter(
        code=test_component.code,
        location__name=test_component.location,
        weight=test_component.weight,
        quantity=test_component.quantity,
    ).exists()

    # checking if the date of component is correctly
    assert test_component.production_date == timezone.now().date()

    # checking if unique code was generated correctly and has exactly 15 digits
    assert len(test_component.unique_code) == 15
