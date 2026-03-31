from django.contrib import admin
from django.urls import path
from inventory.views import *

urlpatterns = [
    path('change_location/', ChangeLocationView.as_view(), name='change_location'),
    path('release_component/', ReleasedComponentView.as_view(), name='release_component'),
    path('check_location/', CheckLocationView.as_view(), name='check_location'),
    path('check_component/', CheckComponentView.as_view(), name='check_component'),
    path('check_component/grouped/', CheckComponentGroupedView.as_view(), name='check_component_grouped'),
    path('quantity_in_department/', ShowQuantityInDepartmentView.as_view(), name='show_quantity_in_department'),
    path('quantity_in_stock/', ShowQuantityInStockView.as_view(), name='show_quantity_in_stock'),

]