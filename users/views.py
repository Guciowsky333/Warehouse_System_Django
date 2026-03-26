from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsManager
from users.serializers import CustomUserSerializer
from users.services import create_custom_user


# Create your views here.

class CreateCustomUserView(APIView):

    permission_classes = [IsAuthenticated, IsManager]    #<-- This view is allow only for user with manager role
    serializer_class = CustomUserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            result = create_custom_user(serializer.validated_data)
            return Response(result, status=201)
        return Response(serializer.errors, status=400)


