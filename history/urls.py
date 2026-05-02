from django.urls import path

from history.views import ComponentsHistoryView

urlpatterns = [
    path("", ComponentsHistoryView.as_view(), name="component_history"),
]
