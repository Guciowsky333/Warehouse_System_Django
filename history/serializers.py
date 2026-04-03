
from history.models import *
from rest_framework import serializers
from history.models import *

class ComponentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentHistory
        fields = ['code', 'unique_code','previous_location','current_location', 'quantity', 'weight', 'full_name', 'date', 'action']