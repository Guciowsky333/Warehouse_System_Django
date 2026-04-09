from rest_framework import serializers
from list_LPT.models import ListLPT, OrderComponent
from rest_framework.serializers import ModelSerializer
from django.db.models import Sum

class ListLPTSerializer(serializers.Serializer):
    """
    This serializer is used to validation department that user provided in body
    """
    department = serializers.ChoiceField(choices=ListLPT.DEPARTMENTS)


    def to_internal_value(self, data):
        if isinstance(data.get('department'), int):
            data['department'] = str(data['department'])
        return super().to_internal_value(data)




class OrderComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderComponent
        fields = ['code','quantity','total_boxes','already_released_quantity',
            'already_released_boxes','everything_released']


class ListLPTDetailSerializer(serializers.ModelSerializer):
    order_components = OrderComponentSerializer(many=True, read_only=True)
    user = serializers.SerializerMethodField()
    total_boxes_in_list = serializers.SerializerMethodField()
    total_boxes_in_list_released = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.full_name()

    def get_total_boxes_in_list(self, obj):
        result = obj.order_components.all().aggregate(
            total=Sum('total_boxes')
        )
        return result['total']

    def get_total_boxes_in_list_released(self, obj):
        result = obj.order_components.all().aggregate(
            total=Sum('total_boxes_released')
        )
        return result['total']

    class Meta:
        model = ListLPT
        fields = [
            'user',
            'department',
            'date',
            'closed'
            'total_boxes_in_list',
            'total_boxes_in_list_released',
            'order_components',
        ]





