from django.contrib import admin
from django.urls import path
from inventory.views import ChangeLocationView

urlpatterns = [
    path('change_location/', ChangeLocationView.as_view(), name='change_location'),
]