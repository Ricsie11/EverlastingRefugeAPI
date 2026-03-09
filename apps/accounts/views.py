import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from apps.core.permissions import IsAdminOrSuperUser, IsSuperUser
from apps.core.choices import AppRole
from apps.accounts.models import UserRole
from apps.accounts.utils import has_role

User = get_user_model()


class CreateUserView(APIView):

    permission_classes = [IsAdminOrSuperUser]

    def post(self, request):

        email = request.data.get("email")
        role = request.data.get("role", AppRole.USER)

        if role == AppRole.SUPERUSER:
            return Response({"error": "Cannot create superuser"}, status=403)

        if role == AppRole.ADMIN and not has_role(request.user, AppRole.SUPERUSER):
            return Response({"error": "Only superusers can create admins"}, status=403)

        if not email:
            email = f"user-{uuid.uuid4()}@placeholder.com"

        user = User.objects.create_user(
            username=email,
            email=email,
            password="tempPassword123"
        )

        UserRole.objects.create(user=user, role=role)

        return Response({"message": "User created"})
