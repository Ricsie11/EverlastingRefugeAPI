from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    EmailTokenObtainPairView,
    JoinGroupView,
)

urlpatterns = [
    # Authentication
    path("api/auth/register/", UserRegistrationView.as_view(), name="register"),
    path("api/auth/login/", EmailTokenObtainPairView.as_view(), name="login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/groups/join/", JoinGroupView.as_view(), name="join-group"),
]