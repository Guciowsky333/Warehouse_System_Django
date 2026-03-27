from django.db import models
from inventory.services import generate_unique_code
from django.db.models import Sum

# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=6)

    def __str__(self):
        return self.name

    @property
    def total_weight(self):
        ''' This method returns the total weight of this location.
        This will be useful for checking if the location is too heavy. Maximum weight is 800 kg.'''

        result = self.components.aggregate(total_weight=Sum('weight'))
        return result['total_weight'] or 0




class Component(models.Model):
    code = models.CharField(max_length=10)
    unique_code = models.CharField(max_length=15, unique=True, default=generate_unique_code)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='components')
    weight = models.FloatField()
    quantity = models.IntegerField()
    production_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.code


