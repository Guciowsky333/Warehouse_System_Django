from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class CustomUser(AbstractUser):
    ROLES = {
        "warehouseman":"warehouseman",
        "foreman":"foreman",
        "manager":"manager",
    }
    role = models.CharField(max_length=20, choices=ROLES)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"

