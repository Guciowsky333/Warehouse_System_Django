from rest_framework import serializers
from inventory.models import *

class ChangeLocationSerializer(serializers.Serializer):
    unique_code = serializers.CharField(max_length=15)
    location_name = serializers.CharField(max_length=6)

class ReleasedComponentSerializer(serializers.Serializer):
    unique_code = serializers.CharField(max_length=15)
    department = serializers.CharField(max_length=4)

class UndoComponentSerializer(serializers.Serializer):
    unique_code = serializers.CharField(max_length=15)
    location_name = serializers.CharField(max_length=6)





class ComponentSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name')
    class Meta:
        model = Component
        fields = ['code', 'unique_code', 'quantity', 'production_date', 'location_name']

