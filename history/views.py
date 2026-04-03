
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from history.models import ComponentHistory
from history.serializers import ComponentHistorySerializer
from history.services import *
# Create your views here.


class ComponentsHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ComponentHistorySerializer

    def get(self, request):
        code = request.query_params.get('code')
        unique_code = request.query_params.get('unique_code')
        user_name = request.query_params.get('user_name')
        action = request.query_params.get('action')

        try:
            result = history(code, unique_code, user_name, action)
            message, queryset = result['message'], result['history']

            serializer = ComponentHistorySerializer(queryset, many=True)

            return Response({
                'message': message,
                'history': serializer.data
            })


        except NotFound as e:
            return Response({
                'message':str(e),
            }, status=404)

        except ValueError as e:
            return Response({
                'message':str(e),
            }, status=400)