from rest_framework import serializers
from list_LPT.models import ListLPT

class ListLPTSerializer(serializers.Serializer):
    department = serializers.ChoiceField(choices=ListLPT.DEPARTMENTS)

    def to_internal_value(self, data):
        if isinstance(data.get('department'), int):
            data['department'] = str(data['department'])
        return super().to_internal_value(data)