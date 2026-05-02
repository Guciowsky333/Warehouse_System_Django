from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("full_name", "role")

    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role", {"fields": ("role",)}),
        ("first_name", {"fields": ("first_name",)}),
        ("last_name", {"fields": ("last_name",)}),
    )
