from django.urls import path
from .views import LoginView, RegisterAdminView, ProjectControlView, UserCreationView, TaskControlView, GenerateReport

urlpatterns = [
    path('login/', LoginView.as_view(), name='login_view'),
    path('registeradmin/', RegisterAdminView.as_view(), name='register_admin'),
    path('project/<str:action>/',
         ProjectControlView.as_view(), name='project_control'),
    path('task/<str:action>/',
         TaskControlView.as_view(), name='task_control'),
    path('createuser/<str:usertype>/',
         UserCreationView.as_view(), name='create_user'),
    path('analytics/<str:reporttype>/',
         GenerateReport.as_view(), name='create_user'),
]
