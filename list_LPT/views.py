from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from list_LPT.models import *
from list_LPT.services import *
from list_LPT.permissions import IsForemanOrHigher

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
    permission_classes = [IsAuthenticated, IsForemanOrHigher]

    def post(self, request):
        components = request.data.get('components')

        try:
            result = create_list(components)
            return Response(result, status=20)

        except ValueError as e:
            return Response({
                'message': str(e)
            }, status=400)

        except NotFound as e:
            return Response({
                'message': str(e)
            },status=404)