from django.contrib import admin
from inventory.models import Location, Component, ReleasedComponent

# Register your models here.

@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    def location_name(self, obj):
        return obj.location.name
    list_display = ('code', 'unique_code', 'location_name')


@admin.register(ReleasedComponent)
class ReleasedComponentAdmin(admin.ModelAdmin):
    list_display = ('code', 'unique_code', 'department')

admin.site.register(Location)

