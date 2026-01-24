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
    Attendance,
    Event
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
    AttendanceReportSerializer,
    EventSerializer
)
import logging
from django.db import IntegrityError, transaction

logger = logging.getLogger(__name__)

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
    serializer_class = UserSerializer  # Serializer for user data

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
        serializer.save(created_by=self.request.user)


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
            return Response({"detail": "No group assigned"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch the latest active and valid QR code for the group
        qr = AttendanceQR.objects.filter(
            group=request.user.group,
            is_active=True,
            expires_at__gte=timezone.now()
        ).last()

        # If no active QR exists
        if not qr:
            return Response({"detail": "No active QR"}, status=status.HTTP_404_NOT_FOUND)
        
         # Audit log
        logger.info(
            f"[QR_ACCESS] admin={request.user.id} group={qr.group.id} qr={qr.id}"
        )
        
        # Return QR token
        return Response({"token": qr.token, "expires_at":qr.expires_at})


class ScanQRView(APIView):
    """
    Scan a QR code and mark attendance for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        """
        Validate the QR token and record attendance
        if all security checks pass.
        """
        token = request.data.get("token")

        # Token must be provided
        if not token:
            return Response({"detail": "Token required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate QR token and expiration
        qr = (
            AttendanceQR.objects.select_for_update()
            .select_related("group")
            .filter(
                token=token,
                is_active=True,
                expires_at__gte=timezone.now(),
            )
            .first()
        )

        # Invalid or expired QR
        if not qr:
            return Response({"detail": "Invalid or expired QR"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure user belongs to the same group as the QR
        if request.user.group != qr.group:
            return Response({"detail": "QR does not belong to your group"}, status=status.HTTP_403_FORBIDDEN)
        
        try:
        # Record attendance (prevents duplicate scans)
            Attendance.objects.create(
            user=request.user,
            group=qr.group,
            qr_session=qr
        )
        except IntegrityError:
             # Relies on DB unique constraint
            return Response({"detail":"Attendance already recorded"}, status=status.HTTP_409_CONFLICT)
        
        logger.info(
            f"[ATTENDANCE] user={request.user.id} group={qr.group.id} qr={qr.id}"
        )

        return Response({"detail":"Attendance recorded"}, status=status.HTTP_201_CREATED)
    

# =======================
# Attendance Report (ADMIN)
# =======================
class AttendanceReportView(ListAPIView):
    """
    Daily attendance report for admin's group
    """
    permission_classes = [IsAdminOrSuperUser]
    serializer_class = AttendanceReportSerializer

    def get_queryset(self):
        today = timezone.now().date()
        return Attendance.objects.filter(
            scanned_at__date=today,
            group=self.request.user.group
        ).select_related("user", "group")
    

class PublicEventListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        now = timezone.now()

        upcoming = Event.objects.filter(date__gte=now, is_active=True).order_by("date")
        past = Event.objects.filter(date__lt=now).order_by("-date")

        return Response({
            "upcoming": EventSerializer(upcoming, many=True).data,
            "past": EventSerializer(past, many=True).data
        })
    


class AdminEventView(APIView):
    permission_classes = [IsAdminOrSuperUser]

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response(
                {"detail": "Event not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EventSerializer(
            event,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, event_id):
        deleted, _ = Event.objects.filter(id=event_id).delete()

        if not deleted:
            return Response(
                {"detail": "Event not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
