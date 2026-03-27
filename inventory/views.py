from django.shortcuts import render
from inventory.services import change_location
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users import permissions


# Create your views here.

class ChangeLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        unique_code = request.data.get('unique_code')
        location = request.data.get('location')

        try:
            result = change_location(unique_code, location)
            return Response(result, status=200)

        except ValueError as e:
            return Response(str(e), status=400)

