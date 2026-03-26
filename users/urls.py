from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import CreateCustomUserView, ResetPasswordView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create/', CreateCustomUserView.as_view(), name='create'),
    path('reset_password/', ResetPasswordView.as_view(), name='reset_password'),
]