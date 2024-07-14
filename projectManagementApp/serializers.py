from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from django.utils.crypto import get_random_string
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from rest_framework.exceptions import AuthenticationFailed
from . models import Project, Task

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get("password")

        if not username or not password:
            raise serializers.ValidationError(
                {"detail": "Invalid username or password."},
                code=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError(
                {"detail": "Invalid username or password."},
                code=status.HTTP_400_BAD_REQUEST,
            )

        refresh = self.get_token(user)

        data = {}
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data


class AdminRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField()
    access_token = serializers.CharField(max_length=150, required=False)

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        access_token = data.get('access_token')
        access_token_fixed = 'abc12345678'

        if not access_token or access_token != access_token_fixed:
            raise AuthenticationFailed(
                {"error": "Enter a valid access token."},
                code=status.HTTP_401_UNAUTHORIZED
            )
        if not email:
            raise serializers.ValidationError(
                {"error": "Email address is required."})

        if not username:
            # If username is not provided, use email address as username
            data['username'] = email

        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(
                {"error": "Username already exists."})

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"error": "Email address already registered."})

        return data

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']

        if not username:
            username = email  # If username is not provided, use email address as username

        password = get_random_string(12)  # Generate random password
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True,
            is_superuser=False
        )

        # Assign admin role
        admin_role = Group.objects.get(name='admin')
        user.groups.add(admin_role)

        # Send email with credentials
        send_mail(
            'Admin User Credentials',
            f'Username: {user.username}\nPassword: {password}',
            '',
            [validated_data['email']],
            fail_silently=False,
        )

        return user


# serializer for project management
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id', 'project_name', 'project_description',
            'assigned_manager',
            'created_datetime', 'status', 'last_updated_datetime'
        ]
        read_only_fields = ['id', 'created_datetime', 'last_updated_datetime']

    def validate(self, data):
        if not data.get('project_name'):
            raise serializers.ValidationError(
                {"project_name": "This field is required."})
        return data

    def create(self, validated_data):
        return Project.objects.create(**validated_data)


# serializer for task management
class TaskSerializer(serializers.ModelSerializer):
    project_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'task_name', 'task_description', 'assigned_team_lead', 'assigned_member',
            'created_datetime', 'status', 'last_updated_datetime', 'project_id'
        ]
        read_only_fields = ['id', 'created_datetime', 'last_updated_datetime']

    def validate(self, data):
        if not data.get('project_id'):
            raise serializers.ValidationError(
                {"error": "Project id is required."})

        return data

    def create(self, validated_data):
        project_id = validated_data.pop('project_id')
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise serializers.ValidationError(
                {"error": f"Project with id {project_id} does not exist."})

        validated_data['project'] = project
        task = Task.objects.create(**validated_data)
        return task


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': True},
        }

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        if not email:
            raise serializers.ValidationError(
                {"error": "Email address is required."})

        if not username:
            data['username'] = email

        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(
                {"error": "Username already exists."})

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"error": "Email address already registered."})

        return data

    def create(self, validated_data):
        password = get_random_string(12)
        username = validated_data['username']
        email = validated_data['email']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True,
            is_superuser=False
        )

        # Send email with credentials
        send_mail(
            'User Credentials',
            f'Username: {user.username}\nPassword: {password}',
            '',
            [validated_data['email']],
            fail_silently=False,
        )

        return user
