from django.contrib import admin
from inventory.models import Location, Component, ReleasedComponent

# Register your models here.

admin.site.register(Location)
admin.site.register(Component)
admin.site.register(ReleasedComponent)
