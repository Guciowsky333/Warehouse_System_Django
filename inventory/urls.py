from django.contrib import admin
from django.urls import path
from inventory.views import ChangeLocationView, ReleasedComponentView, CheckLocationView

urlpatterns = [
    path('change_location/', ChangeLocationView.as_view(), name='change_location'),
    path('release_component/', ReleasedComponentView.as_view(), name='release_component'),
    path('check_location/', CheckLocationView.as_view(), name='check_location'),

]