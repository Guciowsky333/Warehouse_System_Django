from django.contrib import admin
from django.urls import path
from inventory.views import ChangeLocationView, ReleasedComponentView

urlpatterns = [
    path('change_location/', ChangeLocationView.as_view(), name='change_location'),
    path('release_component/', ReleasedComponentView.as_view(), name='release_component'),
]