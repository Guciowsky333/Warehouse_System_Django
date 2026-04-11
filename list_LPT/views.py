from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from list_LPT.models import *
from list_LPT.services import *
from list_LPT.permissions import IsForemanOrHigher
from list_LPT.serializers import *


# Create your views here.

class ValidateComponentView(APIView):
    permission_classes = [IsAuthenticated, IsForemanOrHigher]


    def post(self, request):
        code = request.data.get('code')
        quantity = request.data.get('quantity')

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

    serializer_class = ListLPTSerializer

    def post(self, request):
        components = request.data.get('components')
        department = request.data.get('department')
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

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
