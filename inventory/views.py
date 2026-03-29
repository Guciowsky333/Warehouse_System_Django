from django.shortcuts import render
from inventory.services import change_location, release_component
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from users import permissions


# Create your views here.

class ChangeLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        unique_code = request.data.get('unique_code')
        location = request.data.get('location')

        try:
            result = change_location(unique_code, location)
            return Response({
                "message":result
            },status=200)

        # if user provided inappropriate data
        except ValueError as e:
            return Response({
                "message":str(e)
            }, status=400)

        # if user provided data that not exist in database
        except NotFound as e:
            return Response({
                "message": str(e)
            }, status=404)


class ReleasedComponentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        unique_code = request.data.get('unique_code')
        department = request.data.get('department')

        try:
            result = release_component(unique_code, department)
            return Response({
                "message":result
            }, status=201)

        # if user provided inappropriate data
        except ValueError as e:
            return Response({
                "message":str(e)
            },status=400)

        # if user provided data that not exist in database
        except NotFound as e:
            return Response({
                "message": str(e)
            }, status=404)



