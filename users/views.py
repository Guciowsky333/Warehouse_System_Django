from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from users import serializers
from users.permissions import IsManager
from users.serializers import CustomUserSerializer
from users.services import create_custom_user, reset_password
from drf_spectacular.utils import extend_schema, OpenApiResponse

# Create your views here.

class CreateCustomUserView(APIView):

    permission_classes = [IsAuthenticated, IsManager]

    @extend_schema(
        summary="Create new user",
        description="""
        Create a new user with provided credentials, only user with role manager can create new users.
        
        Important: This endpoint returns password of created user in response, this password is only visible
        ones - save it immediately. Later only way to have access to this account is to restart password in 
        special endpoint.
        
        
        Business rules:
        - Fields first_name, last_name and role are required
        - First_name and last_name must contain only letters
        - Specified role must exist allowed roles (warehouseman, foreman, manager)
        - Request user must has manager role
        - Authentication required 
        """,
        request=CustomUserSerializer,
        responses={
            201: OpenApiResponse(description="User created successfully."),
            400 : OpenApiResponse(description="Validation error."),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Permission denied"),
        }
    )



    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = create_custom_user(serializer.validated_data)

        return Response({
            "message":"User created successfully",
            **result
        }, status=201)




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





