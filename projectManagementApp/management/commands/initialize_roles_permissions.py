from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from projectManagementApp.initialData import INITIAL_PERMISSIONS, INITIAL_ROLES


class Command(BaseCommand):
    help = 'Initialize roles and permissions'

    def handle(self, *args, **kwargs):
        self.create_permissions()
        self.create_roles_and_assign_permissions()
        self.stdout.write(self.style.SUCCESS(
            'Successfully initialized roles and permissions'))

    def create_permissions(self):
        content_type = ContentType.objects.get_for_model(Group)
        for codename, name in INITIAL_PERMISSIONS.items():
            Permission.objects.update_or_create(
                codename=codename,
                defaults={'name': name, 'content_type': content_type},
            )

    def create_roles_and_assign_permissions(self):
        for role_name, permissions in INITIAL_ROLES.items():
            role, created = Group.objects.get_or_create(name=role_name)
            for perm_codename in permissions:
                perm = Permission.objects.get(codename=perm_codename)
                role.permissions.add(perm)
            role.save()
