from rest_framework import serializers
from inventory.models import *

class ComponentSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name')
    class Meta:
        model = Component
        fields = ['unique_code', 'quantity', 'production_date', 'location_name']

