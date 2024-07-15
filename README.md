Features of this application include project management, task management, user role based permissions, and additional permissions for users.

Installation Instructions:
>Create a database and connect it in settings file.
>Add email host, email id and password in settings email configuration
>Run initialize_roles_permissions management commands to initialize application with roles and permissions

Api Endpoints:
1. admin registration
URL: /api/registeradmin/

Method: POST

Description: Register a new admin user with provided email and optional username. The token must be provided for authentication.

Parameters:

email (required): Email address of the admin user.
username (optional): Username for the admin user. If not provided, it defaults to the value of the email.
token (required): Authentication token. Use abc12345678 for testing purposes.

2.Login
URL: /api/login/

Method: POST

Description: Authenticate and log in a user with provided username and password. Returns JWT access token and refresh token on successful login.

Parameters:
username (required): Username of the user.
password (required): Password of the user.

response: jwt access token and refresh token on successfull login

3.Create User
URL: /api/createuser/<usertype>/

Method: POST

Description: Create a new user of specified type with provided email and optional username. Additional permissions can be added for the user. Requires authorization via an access token. checks for permission to create each user types

Parameters:

email (required): Email address of the user.
username (optional): Username for the user. If not provided, it defaults to the value of the email.
additional_permissions (optional, list): List of additional permissions to be assigned to the user.

Headers:
Authorization (required): Bearer token received from the login response.

4.Create Project
URL: /api/project/create/

Method: POST

Description: Create a new project with provided project name, description, assigned manager, and status. Requires authorization via an access token and the user must have the project_control permission.

Parameters:

project_name (required): Name of the project.
project_description (optional): Description of the project.
assigned_manager (optional): Manager assigned to the project.
status (optional): Status of the project.


Headers:
Authorization (required): Bearer token received from the login response.

5.Delete Project
URL: /api/project/delete/

Method: DELETE

Description: Deletes a project with the given ID. Requires authorization via an access token and the user must have the project_control permission.

Parameters:
project_id (required): ID of the project to be deleted.

Headers:
Authorization (required): Bearer token received from the login response.


6.Assign Manager to Project
URL: /api/project/assign_manager/

Method: POST

Description: Assigns a manager with the given ID to the project with the given ID. Requires authorization via an access token and the user must have the project_control permission.

Parameters:
project_id (required): ID of the project to which the manager will be assigned.
manager_id (required): ID of the manager to be assigned to the project.

Headers:
Authorization (required): Bearer token received from the login response.


7.Update Project Status
URL: /api/project/update_status/

Method: POST

Description: Updates the status of a project with the given project ID. User requires update_project permission.

Parameters:
project_id (required): ID of the project to be updated.
status (required): New status of the project.

Headers:
Authorization (required): Bearer token received from the login response.


8.Create Task
URL: /api/task/create/

Method: POST

Description: Create a new task with provided task name, description, assigned member, assigned team lead, and status. Requires authorization via an access token and the user must have the task_control permission.

Parameters:
task_name (required): Name of the task.
task_description (optional): Description of the task.
assigned_member (optional): Member assigned to the task.
assigned_team_lead (optional): Team lead assigned to the task.
status (optional): Status of the task.

Headers:
Authorization (required): Bearer token received from the login response.

9.Delete Task
URL: /api/task/delete/

Method: DELETE

Description: Deletes a task with the given ID. Requires authorization via an access token and the user must have the task_control permission.

Parameters:
task_id (required): ID of the task to be deleted.

Headers:
Authorization (required): Bearer token received from the login response.


10.Assign Member to Task
URL: /api/task/assign_member/

Method: POST

Description: Assigns a member with the given ID to the task with the given ID. Requires authorization via an access token and the user must have the manage_task permission.

Parameters:
task_id (required): ID of the task to which the member will be assigned.
member_id (required): ID of the member to be assigned to the task.

Headers:
Authorization (required): Bearer token received from the login response.


11.Assign Team Lead to Task
URL: /api/task/assign_team_lead/

Method: POST

Description: Assigns a team lead with the given ID to the task with the given ID. Requires authorization via an access token and the user must have the task_control permission.

Parameters:
task_id (required): ID of the task to which the team lead will be assigned.
team_lead_id (required): ID of the team lead to be assigned to the task.

Headers:
Authorization (required): Bearer token received from the login response.


12.Update Task Status
URL: /api/task/update_status/

Method: POST

Description: Updates the status of a task with the given task ID. Requires authorization via an access token. User requires update_task permission.

Parameters:
task_id (required): ID of the task to be updated.
status (required): New status of the task.

Headers:
Authorization (required): Bearer token received from the login response.

13.Project Analytics
URL: /api/analytics/project/

Method: GET

Description: Returns the project report of the given project ID. Requires authorization via an access token and the user must have the project_control permission.

Parameters:
project_id (required): ID of the project for which the report is requested.

Headers:
Authorization (required): Bearer token received from the login response.


14.Task Analytics
URL: /api/analytics/task/

Method: GET

Description: Returns the tasks report of the given team lead. Optionally, if project_id is provided, it returns tasks report of the given team lead within the specified project. Requires authorization via an access token and the user must have the task_control permission.

Parameters:
team_lead_id (required): ID of the team lead for whom the tasks report is requested.
project_id (optional): ID of the project to filter tasks. If provided, returns tasks only for the specified project.

Headers:
Authorization (required): Bearer token received from the login response.

