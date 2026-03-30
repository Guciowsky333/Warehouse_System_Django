from django.contrib import admin
from django.urls import path
from inventory.views import *

urlpatterns = [
    path('change_location/', ChangeLocationView.as_view(), name='change_location'),
    path('release_component/', ReleasedComponentView.as_view(), name='release_component'),
    path('check_location/', CheckLocationView.as_view(), name='check_location'),
    path('check_component/', CheckComponentView.as_view(), name='check_component'),

]