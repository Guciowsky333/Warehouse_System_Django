from django.contrib import admin
from django.urls import path
from list_LPT.views import *



urlpatterns = [
    path('show_all/', ShowAllListLPTAPIView.as_view(), name='show_all'),
    path('validate_component/',ValidateComponentView.as_view(), name='validate_component'),
    path('create_list/',CreateListView.as_view(), name='create_list'),
    path('release_component_from_list/',ReleaseComponentFromListView.as_view(), name='release_component_from_list'),
    path('list/<str:list_number>/details/',ListLPTDetailsView.as_view(), name='list_details'),
    path('list/<str:list_number>/print/',PrintListView.as_view(), name='list_print'),
]