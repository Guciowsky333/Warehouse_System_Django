from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from list_LPT.models import *
from list_LPT.services import *
from list_LPT.permissions import IsForemanOrHigher
from list_LPT.serializers import ListLPTSerializer, ListLPTDetailSerializer


# Create your views here.

class ValidateComponentView(APIView):
    permission_classes = [IsAuthenticated, IsForemanOrHigher]


    def get(self, request):
        code = request.query_params.get('code')
        quantity = request.query_params.get('quantity')

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


