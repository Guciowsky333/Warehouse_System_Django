from idlelib.history import History

from rest_framework import serializers
from history.models import *

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['code', 'unique_code','previous_location','current_location', 'quantity', 'weight', 'full_name', 'date']