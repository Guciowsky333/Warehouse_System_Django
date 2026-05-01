from rest_framework import serializers

from inventory.serializers import ComponentSerializer
from list_LPT.models import ListLPT, OrderComponent


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

class ReleaseComponentFromListSerializer(serializers.Serializer):
    list_number = serializers.CharField(max_length=10)
    unique_code = serializers.CharField(max_length=15)












class ListLPTSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = ListLPT
        fields = ['list_number' , 'department', 'user', 'closed']

    def get_user(self, obj):
        return obj.user.full_name()



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



