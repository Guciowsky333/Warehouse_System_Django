from rest_framework import serializers
from list_LPT.models import ListLPT, OrderComponent
from rest_framework.serializers import ModelSerializer
from inventory.serializers import ComponentSerializer
from django.db.models import Sum


class OrderComponentInputSerializer(serializers.Serializer):
    code = serializers.CharField()
    quantity = serializers.IntegerField()

class CreateListLPTInputSerializer(serializers.Serializer):
    department = serializers.ChoiceField(
        choices= [
            '5000',
            '5500',
            '5800',
            '6000',
        ]
    )
    components = serializers.ListField(
        child=OrderComponentInputSerializer()
    )

class ListLPTSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = ListLPT
        fields = ['list_number' , 'department', 'user', 'closed']

    def get_user(self, obj):
        return obj.user.full_name()



class ListLPTCreateSerializer(serializers.Serializer):
    """
    This serializer is used to validation department that user provided in body
    """
    department = serializers.ChoiceField(choices=ListLPT.DEPARTMENTS)


    def to_internal_value(self, data):
        # If user specified department as int we convert it to string
        if isinstance(data.get('department'), int):
            data['department'] = str(data['department'])
        return super().to_internal_value(data)




class OrderComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderComponent
        fields = ['code','quantity','already_released_quantity','total_boxes',
            'already_released_boxes','everything_released']


class ListLPTDetailsSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    order_components = OrderComponentSerializer(many=True, read_only=True)
    total_boxes_in_list = serializers.SerializerMethodField()
    total_boxes_in_list_released = serializers.SerializerMethodField()



    class Meta:
        model = ListLPT
        fields = [
            'list_number',
            'user',
            'department',
            'date',
            'closed',
            'total_boxes_in_list',
            'total_boxes_in_list_released',
            'order_components',
        ]


    def get_user(self, obj):
        return obj.user.full_name()

    def get_total_boxes_in_list(self, obj):
        """
        Returns new field that has been created in services.py in function "get_optimize_list_order_components"
        """
        return obj.total_boxes_in_list

    def get_total_boxes_in_list_released(self, obj):
        """
        Returns new field that has been created in services.py in function "get_optimize_list_order_components"
        """
        return obj.total_boxes_in_list_released

class PrintListLPTSerializer(serializers.ModelSerializer):
    components = ComponentSerializer(many=True, read_only=True)
    date = serializers.DateTimeField(format='%d.%m.%Y %H:%M')

    class Meta:
        model = ListLPT
        fields = [
            'date',
            'list_number',
            'department',
            'components',
        ]



