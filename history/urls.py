from django.contrib import admin
from django.urls import path
from history.views import *

urlpatterns = [
    path('history_by_code/',ComponentHistoryByCodeView.as_view(), name='history_by_code'),
]