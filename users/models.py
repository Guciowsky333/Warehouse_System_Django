from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class CustomUser(AbstractUser):

    # each employee will have a role at the warehouse that will allow him to do certain things

    # warehouseman - can release, check and change localization of components
    # foreman - can additionally create order lists
    # manager - can additionally clean whole warehouse and create new users

    ROLES = {
        "warehouseman":"warehouseman",
        "foreman":"foreman",
        "manager":"manager",
    }
    role = models.CharField(max_length=20, choices=ROLES)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    def full_name(self):
        """Returns the full name of the employee"""
        return f"{self.first_name} {self.last_name}"


    def __str__(self):
        return self.full_name()

