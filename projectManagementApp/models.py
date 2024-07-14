from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth import get_user_model
from django.utils import timezone


# Create your models here.
class CustomUser(AbstractUser):
    pass

    def add_role(self, role_name):
        group = Group.objects.get(name=role_name)
        self.groups.add(group)

    def remove_role(self, role_name):
        group = Group.objects.get(name=role_name)
        self.groups.remove(group)

    def add_permission(self, perm_codename):
        permission = Permission.objects.get(codename=perm_codename)
        self.user_permissions.add(permission)

    def remove_permission(self, perm_codename):
        permission = Permission.objects.get(codename=perm_codename)
        self.user_permissions.remove(permission)


# Model for project
class Project(models.Model):
    project_name = models.CharField(max_length=255, unique=True)
    project_description = models.TextField(blank=True)
    assigned_manager = models.ForeignKey(get_user_model(
    ), related_name='managed_projects', on_delete=models.SET_NULL, null=True, blank=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, default='Not Started')
    last_updated_datetime = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.project_name


class Task(models.Model):
    project = models.ForeignKey(
        Project, related_name='tasks', on_delete=models.CASCADE)
    task_name = models.CharField(max_length=255)
    task_description = models.TextField(blank=True)
    assigned_team_lead = models.ForeignKey(get_user_model(
    ), related_name='lead_projects', on_delete=models.SET_NULL, null=True, blank=True)
    assigned_member = models.ForeignKey(get_user_model(
    ), related_name='tasks', on_delete=models.SET_NULL, null=True, blank=True)
    created_datetime = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Not Started')
    last_updated_datetime = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.task_name
