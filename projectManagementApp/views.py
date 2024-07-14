from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import CustomTokenObtainPairSerializer, AdminRegistrationSerializer, ProjectSerializer, UserSerializer, TaskSerializer
from django.contrib.auth import get_user_model
from . models import Project, Task
from django.contrib.auth.models import Permission

User = get_user_model()


class RegisterAdminView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AdminRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "success": True,
                "message": "Admin user created successfully.",
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class ProjectControlView(APIView):
    def post(self, request, action):
        user = request.user

        # checking user permission for respective actions
        if action in ['create', 'assign_manager'] and not user.has_perm('auth.project_control'):
            return Response({"error": "User doesnt have the permission to do this action."}, status=status.HTTP_403_FORBIDDEN)
        elif action == 'update_status' and not user.has_perm('auth.update_project'):
            return Response({"error": "User doesnt have the permission to do this action."}, status=status.HTTP_403_FORBIDDEN)

        if action == 'create':
            return self.create_project(request)
        elif action == 'assign_manager':
            return self.assign_manager(request)
        elif action == 'update_status':
            return self.update_status(request)
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, action):
        user = request.user
        if not user.has_perm('auth.project_control'):
            return Response({"error": "User doesnt have the permission to do this action."}, status=status.HTTP_403_FORBIDDEN)
        if action == 'delete':
            return self.delete_project(request)
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

    def create_project(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Project created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete_project(self, request):
        project_id = request.data.get('project_id')
        if not project_id:
            return Response({"error": "Project ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(id=project_id)
            project.delete()
            return Response({"success": True, "message": "Project deleted successfully"}, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

    def assign_manager(self, request):
        project_id = request.data.get('project_id')
        manager_id = request.data.get('manager_id')

        if not project_id or not manager_id:
            return Response({"error": "Project ID and Manager ID are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(id=project_id)
            manager = User.objects.get(id=manager_id)
            if not manager.groups.filter(name='manager').exists():
                return Response({"error": "User is not a manager."}, status=status.HTTP_403_FORBIDDEN)
            project.assigned_manager = manager
            project.save()
            return Response({"success": True, "message": "Manager assigned successfully"}, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "Manager not found."}, status=status.HTTP_404_NOT_FOUND)

    def update_status(self, request):
        project_id = request.data.get('project_id')
        status_value = request.data.get('status')

        if not project_id or not status_value:
            return Response({"error": "Project ID and Status are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(id=project_id)
            project.status = status_value
            project.save()
            return Response({"success": True, "message": "Status updated successfully"}, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class UserCreationView(APIView):
    def post(self, request, usertype, *args, **kwargs):
        user = request.user
        additional_permissions = request.data.get(
            'additional_permissions', [])
        if not request.user.has_perm(f'auth.add_{usertype}'):
            return Response({"error": f"User doesn't have the permission to create user {usertype}."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.add_role(usertype)
            if additional_permissions:
                permissions_to_add = []
                for perm in additional_permissions:
                    try:
                        permission = Permission.objects.get(codename=perm)
                        permissions_to_add.append(permission)
                    except Permission.DoesNotExist:
                        return Response({"error": f"Permission '{perm}' does not exist."}, status=status.HTTP_400_BAD_REQUEST)

                # Assign permissions to the user
                user.user_permissions.add(*permissions_to_add)
                print(
                    f"Added permissions to user '{user.username}': {[perm.codename for perm in permissions_to_add]}")
            else:
                print("no additional perm")
            user.save()
            return Response({"success": True, "message": f"{usertype} user created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class TaskControlView(APIView):
    def post(self, request, action):
        user = request.user

        # checking user permission for respective actions
        if action in ['create', 'assign_team_lead'] and not user.has_perm('auth.task_control'):

            return Response({"error": "User doesnt have the permission to do this action."}, status=status.HTTP_403_FORBIDDEN)
        elif action == 'assign_team_member' and not user.has_perm('auth.manage_task'):
            return Response({"error": "User doesnt have the permission to do this action."}, status=status.HTTP_403_FORBIDDEN)
        elif action == 'update_status' and not user.has_perm('auth.update_task'):
            return Response({"error": "User doesnt have the permission to do this action."}, status=status.HTTP_403_FORBIDDEN)

        if action == 'create':
            return self.create_task(request)
        elif action == 'assign_team_lead':
            return self.assign_team_lead(request)
        elif action == 'assign_member':
            return self.assign_team_member(request)
        elif action == 'update_status':
            return self.update_status(request)
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, action):
        user = request.user
        if not user.has_perm('auth.project_control'):
            return Response({"error": "User doesnt have the permission to do this action."}, status=status.HTTP_403_FORBIDDEN)
        if action == 'delete':
            return self.delete_task(request)
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

    def create_task(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Task created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete_task(self, request):
        task_id = request.data.get('task_id')
        if not task_id:
            return Response({"error": "Task ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            task = Task.objects.get(id=task_id)
            task.delete()
            return Response({"success": True, "message": "Task deleted successfully"}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

    def assign_team_member(self, request):
        task_id = request.data.get('task_id')
        member_id = request.data.get('member_id')

        if not task_id or not member_id:
            return Response({"error": "Task ID and Team Member ID are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            task = Task.objects.get(id=task_id)
            member = User.objects.get(id=member_id)
            if not member.groups.filter(name='team_member').exists():
                return Response({"error": "User is not a team member."}, status=status.HTTP_403_FORBIDDEN)
            task.assigned_member = member
            task.save()
            return Response({"success": True, "message": "Member assigned successfully"}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    def assign_team_lead(self, request):
        task_id = request.data.get('task_id')
        team_lead_id = request.data.get('team_lead_id')

        if not task_id or not team_lead_id:
            return Response({"error": "Task ID and Team Lead ID are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            task = Task.objects.get(id=task_id)
            team_lead = User.objects.get(id=team_lead_id)
            # Check if the authenticated user has the 'team_lead' role
            if not team_lead.groups.filter(name='team_lead').exists():
                return Response({"error": "User is not a team lead."}, status=status.HTTP_403_FORBIDDEN)
            task.assigned_team_lead = team_lead
            task.save()
            return Response({"success": True, "message": "Team Lead assigned successfully"}, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "Team Lead not found."}, status=status.HTTP_404_NOT_FOUND)

    def update_status(self, request):
        task_id = request.data.get('task_id')
        status_value = request.data.get('status')

        if not task_id or not status_value:
            return Response({"error": "Task ID and Status are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            task = Task.objects.get(id=task_id)
            task.status = status_value
            task.save()
            return Response({"success": True, "message": "Status updated successfully"}, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)


@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
class GenerateReport(APIView):
    def get(self, request, reporttype):
        user = request.user
        if reporttype == 'project':
            if not user.has_perm('auth.project_control'):
                return Response({"error": "User doesnt have the permission to generate project report."}, status=status.HTTP_403_FORBIDDEN)
            project_id = request.data.get('project_id')
            if not project_id:
                return Response({"error": "project id is required."}, status=status.HTTP_400_BAD_REQUEST)
            project = get_object_or_404(Project, id=project_id)
            tasks = Task.objects.filter(project=project)

            task_data = [
                {
                    "id": task.id,
                    "task name": task.task_name,
                    "task_description": task.task_description,
                    "assigned_team_lead": task.assigned_team_lead.username if task.assigned_team_lead else None,
                    "assigned_member": task.assigned_member.username if task.assigned_member else None,
                    "created_datetime": task.created_datetime,
                    "status": task.status,
                    "last_updated_datetime": task.last_updated_datetime
                }
                for task in tasks
            ]

            response_data = {
                'success': True,
                'data': {
                    'project_name': project.project_name,
                    'description': project.project_description,
                    'start_date': project.created_datetime,
                    'end_date': project.last_updated_datetime,
                    'status': project.status,
                    'tasks': task_data
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
        elif reporttype == 'task':
            if not user.has_perm('auth.task_control'):
                return Response({"error": "User doesnt have the permission to generate task report."}, status=status.HTTP_403_FORBIDDEN)
            project_id = request.data.get('project_id')
            team_lead_id = request.data.get('team_lead_id')

            if not team_lead_id:
                return Response({"error": "Team Lead ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            team_lead = get_object_or_404(User, id=team_lead_id)
            if not team_lead.groups.filter(name='team_lead').exists():
                return Response({"error": "User is not a team lead."}, status=status.HTTP_400_BAD_REQUEST)

            tasks = Task.objects.filter(assigned_team_lead_id=team_lead_id)

            if project_id:
                project = get_object_or_404(Project, id=project_id)
                tasks = tasks.filter(project=project)

            task_data = [
                {
                    "id": task.id,
                    'task name': task.task_name,
                    "task_description": task.task_description,
                    "assigned_member": task.assigned_member.username if task.assigned_member else None,
                    "created_datetime": task.created_datetime,
                    "status": task.status,
                    "last_updated_datetime": task.last_updated_datetime,
                    "project": task.project.project_name
                }
                for task in tasks
            ]

            response_data = {
                'success': True,
                'data': task_data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        else:
            return Response({"error": "Invalid report type."}, status=status.HTTP_400_BAD_REQUEST)
