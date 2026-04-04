from django.db import models
from list_LPT.utils import generate_number_of_list

# Create your models here.

class LPT_list(models.Model):
    list_number = models.CharField(default=generate_number_of_list, unique=True, max_length=10)
    closed = models.BooleanField(default=False)

    def __str__(self):
        return self.list_number

class OrderComponent(models.Model):
    list = models.ForeignKey(LPT_list, on_delete=models.CASCADE)
    code = models.CharField()
    quantity = models.IntegerField()
    everything_released = models.BooleanField(default=False)
