
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from history.models import ComponentHistory
from history.serializers import *
from history.services import *
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
# Create your views here.


class ComponentsHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Show history of components',
        description="""
        Returns whole history of components by filters such as : code, unique_code or user_name,'
        User has to specified only one filter and he also can specified action filter to
        see only components with this action but this filed can be omitted and then user will see components 
        with all actions.Allowed actions (change_location, component_release, component_undo).
        
        Business rules:
        - User must specify one filter, allowed filters (code, unique_code, user_name)
        - If user specify action he must specify correct action , allowed actions (change_location, component_release, component_undo)
        - History with provided code, unique_code or user_name must exist
        - Authentication required
        """,
        parameters=[
            OpenApiParameter(name='code',type=str, required=False),
            OpenApiParameter(name='unique_code',type=str, required=False),
            OpenApiParameter(name='user_name',type=str, required=False),
            OpenApiParameter(name='action',type=str, required=False),
            OpenApiParameter(name='page', type=int, required=False, description='Page number'),
        ],
        responses={
            200: OpenApiResponse(description='Returns whole history of components'),
            400: OpenApiResponse(description='Validation error'),
            404: OpenApiResponse(description='History with provided filters not found'),
            401: OpenApiResponse(description='Unauthorized'),
        }
        
    )



    def get(self, request):

        # Validate specified filters
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
            paginator.page_size = 10
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