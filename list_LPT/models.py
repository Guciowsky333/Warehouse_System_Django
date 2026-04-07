from django.db import models
from list_LPT.utils import generate_number_of_list
from users.models import CustomUser

# Create your models here.

class ListLPT(models.Model):
    DEPARTMENTS = {
        "5000": "5000",
        "5500": "5500",
        "5800": "5800",
        "6000": "6000",
    }


    list_number = models.CharField(default=generate_number_of_list, unique=True, max_length=10)
    department = models.CharField(max_length=4, choices=DEPARTMENTS)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    closed = models.BooleanField(default=False)




    def __str__(self):
        return self.list_number

class OrderComponent(models.Model):
    """
    This model represents code of component and quantity that user's with foreman or manager role
    want to order form warehouse
    """
    list = models.ForeignKey(ListLPT, on_delete=models.CASCADE, related_name='order_components')
    code = models.CharField()
    quantity = models.IntegerField()

    # if whole ordered quantity of this component in list will be released this field will be True
    everything_released = models.BooleanField(default=False)

    def __str__(self):
        return self.code
