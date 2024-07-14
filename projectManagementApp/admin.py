from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import CustomUser, Project, Task
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name',
                    'last_name', 'is_staff', 'is_active')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Permission)
admin.site.register(Project)
admin.site.register(Task)
