from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser, Group, HouseFellowship, Attendance, Event


# ============================
# JWT LOGIN SERIALIZER (EMAIL)
# ============================
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer to authenticate users using email instead of username.
    """
    username_field = 'email'


# ============================
# USER READ SERIALIZER
# ============================
class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for reading user data.
    Used by admins to list users or view profiles.
    """
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "role",
            "group",
        ]
        read_only_fields = ["role", "group"]


# ============================
# USER REGISTRATION SERIALIZER
# ============================
class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new users.
    Handles password hashing securely.
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "password",
            "phone_number",
        ]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            phone_number=validated_data.get("phone_number"),
        )
        return user


# ============================
# GROUP SERIALIZER
# ============================
class GroupSerializer(serializers.ModelSerializer):
    """
    Serializer for church groups.
    """
    class Meta:
        model = Group
        fields = [
            "id",
            "name",
            "description",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at"]


# ============================
# HOUSE FELLOWSHIP SERIALIZER
# ============================
class HouseFellowshipSerializers(serializers.ModelSerializer):
    """
    Serializer for house fellowship centers.
    """
    class Meta:
        model = HouseFellowship
        fields = [
            "id",
            "fellowship_name",
            "location",
            "fellowship_leader_name",
            "leader_contact",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at"]


class JoinGroupSerializer(serializers.ModelSerializer):
    group_id = serializers.IntegerField()


    def validate(self, attrs):
        user = self.context["request"].user


        if user.group is not None:
            raise serializers.ValidationError(
                "You are already assigned to a group."
            )
        
        try:
            group = Group.objects.get(id=attrs["group_id"])
        except Group.DoesNotExist:
            raise serializers.ValidationError("Group not found.")

        attrs["group"] = group
        return attrs 
    
    def save(self, **kwargs):
        user = self.context["request"].user
        user.group = self.validated_data["group"]
        user.save()
        return user
    

class AttendanceReportSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email")
    group_name = serializers.CharField(source="group.name")

    class Meta:
        model = Attendance
        fields = [
            "id",
            "user_name",
            "group_name",
            "scanned_at",
        ]

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "date",
            "image",
            "is_active",
        ]