from django.contrib import admin
from django.urls import path
from list_LPT.views import *



urlpatterns = [
    path('validate_component/',ValidateComponentView.as_view(), name='validate_component'),
    path('create_list/',CreateListView.as_view(), name='create_list'),
    path('release_component_from_list/',ReleaseComponentFromListView.as_view(), name='release_component_from_list'),
]