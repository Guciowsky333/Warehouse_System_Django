from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from users import serializers
from users.permissions import IsManager
from users.serializers import CustomUserSerializer
from users.services import create_custom_user, reset_password


# Create your views here.

class CreateCustomUserView(APIView):

    permission_classes = [IsAuthenticated, IsManager]    #<-- This view is allow only for user with manager role
    serializer_class = CustomUserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            result = create_custom_user(serializer.validated_data)

            return Response({
                "message":"User created successfully",
                **result
            }, status=201)

        return Response(serializer.errors, status=400)


class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def patch(self, request):
        username = request.data.get('username')

        #if user exists
        try:
            result = reset_password(username=username)
            return Response({
                "message":"Password reset successfully",
                **result
            },status=200)


        # if user dont exist
        except ValueError as e:
            return Response({
                "message":str(e),
            },status=404)



