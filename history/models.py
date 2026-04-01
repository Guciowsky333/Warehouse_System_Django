from django.db import models
from users.models import CustomUser

# Create your models here.
class ComponentHistory(models.Model):
    ACTIONS ={
        "change_location":"change_location",
        "component_release":"component_release",
        "component_undo":"component_undo",
    }

    action = models.CharField(choices=ACTIONS, max_length=17)

    code = models.CharField(max_length=10)
    unique_code = models.CharField(max_length=15)
    quantity = models.IntegerField()
    weight = models.FloatField()

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    full_name = models.CharField(max_length=100)

    date = models.DateTimeField(auto_now_add=True)

    previous_location = models.CharField(max_length=100)
    current_location = models.CharField(max_length=100)

    def __str__(self):
        return self.code

