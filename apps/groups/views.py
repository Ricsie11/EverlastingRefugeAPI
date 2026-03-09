from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from apps.core.permissions import IsAdminOrSuperUser
from .models import Group
from .serializers import GroupSerializer


class GroupViewSet(ModelViewSet):

    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get_permissions(self):

        if self.action in ["create", "update", "destroy"]:
            return [IsAdminOrSuperUser()]

        return [IsAuthenticatedOrReadOnly()]
