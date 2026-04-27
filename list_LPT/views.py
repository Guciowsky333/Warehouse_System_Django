from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from list_LPT.models import *
from list_LPT.services import *
from list_LPT.permissions import IsForemanOrHigher
from list_LPT.serializers import *
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter


# Create your views here.
class ShowAllListLPTAPIView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = ListLPTSerializer

    def get(self, request):
        queryset = ListLPT.objects.all().order_by('-date')

        # We use pagination here because in the future we can have a lot of lists in the database

        paginator = PageNumberPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(queryset, request)

        serializer = self.serializer_class(page, many=True)

        return paginator.get_paginated_response(serializer.data)






class ValidateComponentView(APIView):
    permission_classes = [IsAuthenticated, IsForemanOrHigher]

    @extend_schema(
        summary='Validate single component',
        description="""
        Validates a single component before adding it to the order list.

        This endpoint is designed for real-time validation during list creation.
        Frontend should call this endpoint after each component is entered by the user,
        so they receive immediate feedback without waiting for the entire list to be submitted.

        Business rules:
        - Fields code and quantity are required
        - Component with provided code must exist in warehouse
        - Quantity cannot exceed available stock
        - Component cannot be already assigned to another list
        - User must has at least foreman role or higher
        - Authentication required
        """,
        request=OrderComponentInputSerializer,
        responses={
            200: OpenApiResponse(description='Validation was successful'),
            400 : OpenApiResponse(description='User want order too much quantity of component'),
            404: OpenApiResponse(description='Code not found'),
            401: OpenApiResponse(description='Unauthorized'),
            403: OpenApiResponse(description='Permission denied'),

        }
    )


    def post(self, request):
        serializer = OrderComponentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.data['code']
        quantity = serializer.data['quantity']

        try:
            validate_component(code, quantity)
            return Response({
                'message': 'OK'
            }, status=200)


        except ValueError as e:
            return Response({
                'message': str(e)
            },status=400)


        except NotFound as e:
            return Response({
                'message': str(e)
            },status=404)

class CreateListView(APIView):

    # only users with foreman role or higher are albe to create a list
    permission_classes = [IsAuthenticated, IsForemanOrHigher]

    @extend_schema(
        summary='Create list with provided components',
        description="""
        This endpoint creates a new list with provided components and department.
        
        Each component goes through the same validation as in ValidateComponentView, so even 
        if user skip ValidateComponentView endpoint components will still goes through validations
        
        Business rules:
        - Fields components and department are required
        - Department must be one of : 5000, 5500, 5800, 6000
        - Each component must exist in the warehouse with lower or equal quantity that user want to order 
        - User cannot order the same code of component more than once per list 
        - User must have at least foreman role or higher to create a list
        - Authentication required
        """,
        request=CreateListLPTInputSerializer,
        responses={
            201: OpenApiResponse(description='Create list was successful'),
            400 : OpenApiResponse(description='Validation error / code has been already on this list / dont enough quantity at stock'),
            404: OpenApiResponse(description='Code not found'),
            401: OpenApiResponse(description='Unauthorized'),
            403: OpenApiResponse(description='Permission denied'),

        }
    )



    def post(self, request):
        serializer = CreateListLPTInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        components = serializer.data['components']
        department = serializer.data['department']
        user = request.user


        try:
            result = create_list(components, department, user)
            return Response(result, status=201)

        except ValueError as e:
            return Response({
                'message': str(e)
            }, status=400)

        except NotFound as e:
            return Response({
                'message': str(e)
            },status=404)



class ReleaseComponentFromListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        list_number = request.data.get('list_number')
        unique_code = request.data.get('unique_code')
        user = request.user

        try:
            result = released_component_from_list(list_number, unique_code, user)
            return Response(result, status=201)

        except ValueError as e:
            return Response({
                'message': str(e)
            },status=400)

        except NotFound as e:
            return Response({
                'message': str(e)
            }, status=404)

class ListLPTDetailsView(APIView):
    """This endpoint is used to show users detail about provided list such as
    how many components are in this list and how many has been released so far, and more"""


    permission_classes = [IsAuthenticated]
    serializer_class = ListLPTDetailsSerializer

    def get(self, request, list_number):

        try:
            result = get_optimize_list_order_components(list_number)
            serializer = self.serializer_class(result)
            return Response(serializer.data, status=200)

        except NotFound as e:
            return Response({
                'message': str(e)
            }, status=404)

        except ValueError as e:
            return Response({
                'message': str(e)
            }, status=400)





class PrintListView(APIView):
    """
    This endpoint is used to print whole physical list on the warehouse

    It will be useful for the warehouse workers to have physical list with all components
    that they have to release sorted by location
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PrintListLPTSerializer

    def get(self, request, list_number):

        try:
            result = get_optimize_list_components(list_number)
            serializer = self.serializer_class(result)
            return Response(serializer.data, status=200)

        except NotFound as e:
            return Response({
                'message': str(e)
            }, status=404)

        except ValueError as e:
            return Response({
                'message': str(e)
            }, status=400)
