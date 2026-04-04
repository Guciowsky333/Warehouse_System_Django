from django.db import models
from list_LPT.utils import generate_number_of_list

# Create your models here.

class ListLPT(models.Model):
    list_number = models.CharField(default=generate_number_of_list, unique=True, max_length=10)
    closed = models.BooleanField(default=False)

    def __str__(self):
        return self.list_number

class OrderComponent(models.Model):
    """
    This model represents code of component and quantity that user's with foreman or manager role
    want to order form warehouse
    """
    list = models.ForeignKey(ListLPT, on_delete=models.CASCADE)
    code = models.CharField()
    quantity = models.IntegerField()

    # if whole ordered quantity will be released this field will be True
    everything_released = models.BooleanField(default=False)
