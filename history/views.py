
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from history.models import ComponentHistory
from history.serializers import *
from history.services import *
from rest_framework.pagination import PageNumberPagination
# Create your views here.


class ComponentsHistoryView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request):
        query_serializer = ComponentHistoryQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        data = query_serializer.data

        code = data.get('code')
        unique_code = data.get('unique_code')
        user_name = data.get('user_name')
        action = data.get('action')

        try:
            result = history(code, unique_code, user_name, action)
            message, queryset = result['message'], result['history']

            paginator = PageNumberPagination()
            paginator.page_size = 20
            page = paginator.paginate_queryset(queryset, request)

            response_serializer = ComponentHistorySerializer(page, many=True)

            response = paginator.get_paginated_response(response_serializer.data)
            response.data['message'] = message

            return response



        except NotFound as e:
            return Response({
                'message':str(e),
            }, status=404)

        except ValueError as e:
            return Response({
                'message':str(e),
            }, status=400)