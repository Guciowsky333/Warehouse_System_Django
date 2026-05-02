from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsManager
from users.serializers import CustomUserSerializer, ResetPasswordSerializer
from users.services import create_custom_user, reset_password

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
            400: OpenApiResponse(description="Validation error."),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Permission denied"),
        },
    )
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        first_name = serializer.validated_data["first_name"]
        last_name = serializer.validated_data["last_name"]
        role = serializer.validated_data["role"]

        result = create_custom_user(first_name, last_name, role)

        return Response({"message": "User created successfully", **result}, status=201)


class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    @extend_schema(
        summary="Reset user password",
        description="""
        Generates new password for user with provided username and set up new password
        and return it in a response.
        
        Important: This endpoint returns new password in response only ones - save it immediately 
        to access to this account, if you don't save it only way to recover this account will be to 
        change the password of this account again in this endpoint by providing username.
        
        Business rules:
        - Fields username is required
        - User with specified username must exist
        - Request user must has manager role
        - Authentication required 
        """,
        request=ResetPasswordSerializer,
        responses={
            200: OpenApiResponse(description="Password reset successfully."),
            404: OpenApiResponse(description="User not found."),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Permission denied"),
        },
    )
    def patch(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.data["username"]

        try:
            result = reset_password(username=username)
            return Response({"message": "Password reset successfully", **result}, status=200)

        except NotFound as e:
            return Response(
                {
                    "message": str(e),
                },
                status=404,
            )
