from django.contrib import admin
from django.urls import path
from history.views import *

urlpatterns = [
    path('',ComponentsHistoryView.as_view(), name='component_history'),
]