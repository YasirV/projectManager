INITIAL_PERMISSIONS = {
    'add_manager': 'Can add and manage manager role',
    'add_team_lead': 'Can add and manage team lead role',
    'add_team_member': 'Can add and manage team member role',
    'project_control': 'Can create edit and delete projects and generate project based report',
    'update_project': 'can update project status',
    'task_control': 'Can create edit and delete tasks and assign task to  generate task based report',
    'manage_task': 'can view task and assign task to team members',
    'update_task': 'can update task status',
}

INITIAL_ROLES = {
    'admin': list(INITIAL_PERMISSIONS.keys()),
    'manager': [perm for perm in INITIAL_PERMISSIONS if perm not in ('add_manager', 'project_control')],
    'team_lead': ['manage_task', 'update_task', 'add_team_member'],
    'team_member': ['update_task'],
}
