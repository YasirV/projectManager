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

2.Login Endpoint
URL: /api/login/

Method: POST

Description: Authenticate and log in a user with provided username and password. Returns JWT access token and refresh token on successful login.

Parameters:
username (required): Username of the user.
password (required): Password of the user.

response: jwt access token and refresh token on successfull login

3.Create User Endpoint
URL: /api/createuser/<usertype>/

Method: POST

Description: Create a new user of specified type with provided email and optional username. Additional permissions can be added for the user. Requires authorization via an access token. checks for permission to create each user types

Parameters:

email (required): Email address of the user.
username (optional): Username for the user. If not provided, it defaults to the value of the email.
additional_permissions (optional, list): List of additional permissions to be assigned to the user.

Headers:
Authorization (required): Bearer token received from the login response.

4.Create Project Endpoint
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
