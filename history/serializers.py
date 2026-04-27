
from history.models import *
from rest_framework import serializers
from history.models import *

class ComponentHistoryQuerySerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    unique_code = serializers.CharField(required=False, max_length=15)
    user_name = serializers.CharField(required=False)
    action = serializers.ChoiceField(
        choices=[
            'change_location',
            'component_release',
            'component_undo'
        ],
        required=False
    )

    def validate(self, attrs):
        filters = [
            attrs.get('code'),
            attrs.get('unique_code'),
            attrs.get('user_name'),
        ]

        # Checking if user specified only one filter to check history (code, unique_code or user_name)
        # "action" is additional filter, and it can be omitted at all or use with another filters at the same time
        if sum(bool(x) for x in filters) != 1:
            raise serializers.ValidationError('Provide exactly one of: code, unique_code, user_name.')

        return attrs









class ComponentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentHistory
        fields = ['code', 'unique_code','previous_location','current_location', 'quantity', 'weight', 'full_name', 'date', 'action']