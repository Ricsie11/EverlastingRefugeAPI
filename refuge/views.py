from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from rest_framework import status
from .models import (
    CustomUser,
    Group,
    HouseFellowship,
    AttendanceQR,
    Attendance
)
from .permissions import IsAdminOrSuperUser
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    UserSerializer,
    GroupSerializer,
    HouseFellowshipSerializers,
    UserRegistrationSerializer,
    EmailTokenObtainPairSerializer,
    JoinGroupSerializer,
    AttendanceReportSerializer
)
import logging
from django.db import IntegrityError

# =======================
# User Registration Views
# =======================
class UserRegistrationView(APIView):
    """
    Register a new user.
    Public endpoint.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "detail":"User registered successfully!"
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# =======================
# Email Token View
# =======================
class EmailTokenObtainPairView(TokenObtainPairView):
    """
    JWT login view using email instead of username.
    """
    serializer_class = EmailTokenObtainPairSerializer
    

# =======================
# User Views
# =======================
class UserListView(ListCreateAPIView):
    """
    List all users or create a new user.
    Access restricted to ADMIN and SUPERUSER only.
    """
    permission_classes = [IsAdminOrSuperUser]
    serializers_class = UserSerializer  # Serializer for user data

    def get_queryset(self):
        """
        Return all users.
        """
        return CustomUser.objects.all()


# =======================
# Group Views
# =======================
class GroupListView(ListCreateAPIView):
    """
    List all groups or create a new group.
    Only ADMIN and SUPERUSER are allowed.
    """
    permission_classes = [IsAdminOrSuperUser]
    serializer_class = GroupSerializer

    def get_queryset(self):
        """
        Return all groups.
        """
        return Group.objects.all()
    
    def perform_create(self, serializer):
        """
        Automatically set the creator of the group
        to the currently authenticated user.
        """
        serializer.save(created_by=self.request.user)


class GroupDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a single group.
    Restricted to ADMIN and SUPERUSER.
    """
    permission_classes = [IsAdminOrSuperUser]
    serializer_class = GroupSerializer

    def get_queryset(self):
        """
        Return all groups for lookup.
        """
        return Group.objects.all()
    

class JoinGroupView(APIView):
    """
    Allows a user to join ONE group only.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = JoinGroupSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "detail": "Successfully Joined group"
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =======================
# House Fellowship Views
# =======================
class HouseFellowshipListView(ListCreateAPIView):
    """
    List all house fellowships or create a new one.
    Access restricted to ADMIN and SUPERUSER.
    """
    permission_classes = [IsAdminOrSuperUser]
    serializer_class = HouseFellowshipSerializers

    def get_queryset(self):
        """
        Return all house fellowship records.
        """
        return HouseFellowship.objects.all()
    
    def perform_create(self, serializer):
        """
        Automatically set the creator of the fellowship
        to the currently authenticated user.
        """
        serializer.save(created_at=self.request.user)


class HouseFellowshipDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a single house fellowship.
    Restricted to ADMIN and SUPERUSER.
    """
    permission_classes = [IsAdminOrSuperUser]
    serializer_class = HouseFellowshipSerializers

    def get_queryset(self):
        """
        Return all house fellowship records for lookup.
        """
        return HouseFellowship.objects.all()


# =======================
# QR Code Views
# =======================
class CurrentQRView(APIView):
    """
    Fetch the currently active QR code token for a user's group.
    Only accessible to ADMIN and SUPERUSER.
    """
    permission_classes = [IsAdminOrSuperUser]

    def get(self, request):
        """
        Return the active QR token for the user's group
        if it exists and has not expired.
        """
        # Ensure the user belongs to a group
        if not request.user.group:
            return Response({"detail": "No group assigned"}, status=400)
        
        # Fetch the latest active and valid QR code for the group
        qr = AttendanceQR.objects.filter(
            group=request.user.group,
            is_active=True,
            expires_at__gte=timezone.now()
        ).last()

        # If no active QR exists
        if not qr:
            return Response({"detail": "No active QR"}, status=404)
        
        # Return QR token (frontend will generate the QR image)
        return Response({"token": qr.token})



logger = logging.getLogger(__name__)

class ScanQRView(APIView):
    """
    Scan a QR code and mark attendance for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Validate the QR token and record attendance
        if all security checks pass.
        """
        token = request.data.get("token")

        # Token must be provided
        if not token:
            return Response({"detail": "Token required"}, status=400)

        # Validate QR token and expiration
        qr = AttendanceQR.objects.filter(
            token=token,
            is_active=True,
            expires_at__gte=timezone.now()
        ).select_related("group").first()

        # Invalid or expired QR
        if not qr:
            return Response({"detail": "Invalid or expired QR"}, status=400)
        
        # Ensure user belongs to the same group as the QR
        if request.user.group != qr.group:
            return Response({"detail": "QR does not belong to your group"}, status=403)
        
        try:
        # Record attendance (prevents duplicate scans)
            Attendance.objects.create(
            user=request.user,
            group=qr.group,
            qr_session=qr
        )
        except IntegrityError:
            return Response({"detail":"Attendance already recorded"}, status=409)
        
        logger.info(
            f"[ATTENDANCE] user={request.user.id} group={qr.group.id} qr={qr.id}"
        )

        return Response({"detail":"Attendance recorded"}, status=201)
    
class AttendanceReportView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    serializer_classes = AttendanceReportSerializer

    def get_queryset(self):
        today = timezone.now().date()
        return Attendance.objects.filter(
            scanned_at__date=today,
            group=self.request.user.group
        ).select_related("user", "group")