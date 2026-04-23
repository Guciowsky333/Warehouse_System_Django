from rest_framework import serializers
from inventory.models import *

class ChangeLocationSerializer(serializers.Serializer):
    unique_code = serializers.CharField()
    location_name = serializers.CharField()

class ReleasedComponentSerializer(serializers.Serializer):
    unique_code = serializers.CharField()
    department = serializers.CharField()





class ComponentSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name')
    class Meta:
        model = Component
        fields = ['code', 'unique_code', 'quantity', 'production_date', 'location_name']

