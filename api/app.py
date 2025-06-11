import io
import json
import os
import shutil
import uuid
from functools import wraps

try:
    from convert import convert_cis_to_attack, combine_results
    from utils import find_file, ClientException
except ImportError:
    from .convert import convert_cis_to_attack, combine_results
    from .utils import find_file, ClientException

from flask import Flask, request, send_file, Response, g
from flask.cli import load_dotenv
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException

load_dotenv()
app = Flask(
    __name__,
    static_folder=os.getenv('FLASK_STATIC_FOLDER'),
    static_url_path='/',
)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

user_management_data = {
    'departments': {},  # {id: {'name': str, 'created_by': str}}
    'department_users': {},  # {dept_id: [user_handles]}
    'next_dept_id': 1,
}

# Parse super admins from environment variable
SUPER_ADMINS = set()
super_admin_env = os.getenv('SUPER_ADMINS', "")
if super_admin_env:
    SUPER_ADMINS = set(
        handle.strip()
        for handle in super_admin_env.split(';')
        if handle.strip()
    )


@app.before_request
def before_request():
    # Parse X-Forwarded-User header
    user_handle = request.headers.get('X-Forwarded-User')
    if user_handle:
        g.current_user = user_handle.strip()
        g.is_super_admin = g.current_user in SUPER_ADMINS
        g.is_department_admin = get_user_department(g.current_user) is not None
    else:
        g.current_user = None
        g.is_super_admin = False
        g.is_department_admin = False


def require_super_admin(f):
    """Decorator to require super admin privileges"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.get('current_user'):
            return {'message': 'Authentication required'}, 401
        if not g.get('is_super_admin'):
            return {'message': 'Super admin privileges required'}, 403
        return f(*args, **kwargs)

    return decorated_function


def require_admin(f):
    """
    Decorator to require admin privileges
    (super admin or department admin)
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.get('current_user'):
            return {'message': 'Authentication required'}, 401
        if not (g.get('is_super_admin') or g.get('is_department_admin')):
            return {'message': 'Admin privileges required'}, 403
        return f(*args, **kwargs)

    return decorated_function


def get_user_department(user_handle):
    """Get the department ID that a user is assigned to (if any)"""
    for dept_id, users in user_management_data['department_users'].items():
        if user_handle in users:
            return dept_id
    return None


def can_access_department(user_handle, department_id):
    """Check if user can access a specific department"""
    if user_handle in SUPER_ADMINS:
        return True
    user_dept = get_user_department(user_handle)
    return user_dept == str(department_id)


@app.get('/api/admin/departments')
@require_admin
def get_departments():
    """
    Get all departments (super admins see all,
    dept admins see only theirs)
    """
    departments = []

    for dept_id, dept_info in user_management_data['departments'].items():
        if g.is_super_admin or can_access_department(g.current_user, dept_id):
            departments.append(
                {
                    'id': dept_id,
                    'name': dept_info['name'],
                    'created_by': dept_info.get('created_by', 'unknown'),
                }
            )

    return {'departments': departments}, 200


@app.post('/api/admin/departments')
@require_super_admin
def create_department():
    """Create a new department (super admin only)"""
    data = request.get_json()

    if not data or not data.get('name'):
        return {'message': 'Department name is required'}, 400

    dept_name = data['name'].strip()

    # Check if department name already exists
    for dept_info in user_management_data['departments'].values():
        if dept_info['name'].lower() == dept_name.lower():
            return {'message': 'Department name already exists'}, 400

    # Create new department
    dept_id = str(user_management_data['next_dept_id'])
    user_management_data['departments'][dept_id] = {
        'name': dept_name,
        'created_by': g.current_user,
    }
    user_management_data['department_users'][dept_id] = []
    user_management_data['next_dept_id'] += 1

    return {
        'department': {
            'id': dept_id,
            'name': dept_name,
            'created_by': g.current_user,
        }
    }, 201


@app.delete('/api/admin/departments/<department_id>')
@require_super_admin
def delete_department(department_id):
    """Delete a department and all its user assignments (super admin only)"""
    if department_id not in user_management_data['departments']:
        return {'message': 'Department not found'}, 404

    # Remove department and its users
    del user_management_data['departments'][department_id]
    if department_id in user_management_data['department_users']:
        del user_management_data['department_users'][department_id]

    return {'message': 'Department deleted successfully'}, 200


@app.get('/api/admin/users')
@require_admin
def get_users():
    """Get all users and their department assignments"""
    users = []

    for dept_id, user_handles in user_management_data[
        'department_users'
    ].items():
        if g.is_super_admin or can_access_department(g.current_user, dept_id):
            dept_name = (
                user_management_data['departments']
                .get(dept_id, {})
                .get('name', 'Unknown')
            )
            for handle in user_handles:
                users.append(
                    {
                        'handle': handle,
                        'department_id': dept_id,
                        'department_name': dept_name,
                    }
                )

    return {'users': users}, 200


@app.post('/api/admin/department-users')
@require_super_admin
def add_user_to_department():
    """Add a user to a department (super admin only)"""
    data = request.get_json()

    if (
        not data
        or not data.get('department_id')
        or not data.get('user_handle')
    ):
        return {'message': 'Department ID and user handle are required'}, 400

    dept_id = data['department_id']
    user_handle = data['user_handle'].strip()

    # Validate department exists
    if dept_id not in user_management_data['departments']:
        return {'message': 'Department not found'}, 404

    # Check if user is already in any department
    current_dept = get_user_department(user_handle)
    if current_dept:
        dept_name = (
            user_management_data['departments']
            .get(current_dept, {})
            .get('name', 'Unknown')
        )
        return {
            'message': f'User is already assigned to department: {dept_name}'
        }, 400

    # Add user to department
    if dept_id not in user_management_data['department_users']:
        user_management_data['department_users'][dept_id] = []

    user_management_data['department_users'][dept_id].append(user_handle)

    return {'message': 'User added to department successfully'}, 201


@app.delete('/api/admin/department-users')
@require_super_admin
def remove_user_from_department():
    """Remove a user from a department (super admin only)"""
    data = request.get_json()

    if (
        not data
        or not data.get('department_id')
        or not data.get('user_handle')
    ):
        return {'message': 'Department ID and user handle are required'}, 400

    dept_id = data['department_id']
    user_handle = data['user_handle'].strip()

    # Validate department exists
    if dept_id not in user_management_data['departments']:
        return {'message': 'Department not found'}, 404

    # Remove user from department
    if dept_id in user_management_data['department_users']:
        try:
            user_management_data['department_users'][dept_id].remove(
                user_handle
            )
            return {
                'message': 'User removed from department successfully'
            }, 200
        except ValueError:
            return {'message': 'User not found in department'}, 404

    return {'message': 'User not found in department'}, 404


@app.get('/api/auth/status')
def get_auth_status():
    """Get current user's authentication status"""
    return {
        'user': g.get('current_user'),
        'is_super_admin': g.get('is_super_admin', False),
        'is_department_admin': g.get('is_department_admin', False),
        'department': (
            get_user_department(g.get('current_user'))
            if g.get('current_user')
            else None
        ),
    }, 200


@app.get('/api/files/<file_id>')
def convert_file(file_id: str) -> tuple[str, int] | Response:
    """Endpoint for retrieving a file by its unique id."""
    file_name, file_path = find_file(UPLOAD_FOLDER, file_id)

    with open(file_path, 'r', encoding='utf-8') as F:
        cis_data = json.load(F)

    attack_data = convert_cis_to_attack(cis_data)

    mem = io.BytesIO(json.dumps(attack_data).encode('utf-8'))

    return send_file(
        mem, as_attachment=True, download_name=f'converted_{file_name}'
    )


@app.get('/api/files', strict_slashes=False)
def get_files_metadata() -> tuple[dict[str, list[dict]], int]:
    """Endpoint for retrieving a list of all stored files' IDs."""
    files_list = []
    # List all directories (file IDs) in the uploads folder
    for file_id in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, file_id)
        if os.path.isdir(file_path):
            # Get the filename from the directory
            dir_files = os.listdir(file_path)
            if len(dir_files) == 1:
                files_list.append({'id': file_id, 'filename': dir_files[0]})
            # TODO else fail?

    return {'files': files_list}, 200


@app.get('/api/files/aggregate')
def aggregate_and_convert_files() -> tuple[str, int] | Response:
    """Endpoint for combining and retrieving multiple files
    by their unique ids."""
    file_ids = request.args.getlist('id')

    if not file_ids:
        return 'No file ids provided', 400

    cis_data_list = []

    for file_id in file_ids:
        _, file_path = find_file(UPLOAD_FOLDER, file_id)

        with open(file_path, 'r', encoding='utf-8') as F:
            cis_data_list.append(json.load(F))

    attack_data = combine_results(cis_data_list)

    mem = io.BytesIO(json.dumps(attack_data).encode('utf-8'))

    return send_file(
        mem,
        as_attachment=True,
        download_name='converted_aggregated_results.json',
    )


@app.post('/api/files/')
def save_file() -> tuple[str, int] | tuple[dict[str, str], int]:
    """Endpoint for uploading, converting and storing the converted file.
    Returns a response with the unique id of the converted file."""
    unique_id = str(uuid.uuid4())
    try:
        if 'file' not in request.files:
            return 'No file part', 400

        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400

        # Secure the filename to be able to safely store it
        filename = secure_filename(file.filename)

        # Secure filename might become empty
        if filename == '':
            return 'Invalid filename', 400

        # Avoid collisions with existing files
        while os.path.exists(os.path.join(UPLOAD_FOLDER, unique_id)):
            unique_id = str(uuid.uuid4())

        # Create a unique directory
        os.makedirs(os.path.join(UPLOAD_FOLDER, unique_id))

        file_path = os.path.join(UPLOAD_FOLDER, unique_id, filename)

        try:
            cis_data = json.load(file.stream)
        except json.JSONDecodeError:
            return 'Invalid file format', 400

        with open(file_path, 'w', encoding='utf-8') as F:
            json.dump(cis_data, F, ensure_ascii=False, indent=2)

        # Send the id of the modified file back to the client
        return {
            'id': unique_id,
            'filename': filename,
        }, 201

    except Exception as e:
        # Clean up on error, remove the directory with all its files
        if os.path.exists(os.path.join(UPLOAD_FOLDER, unique_id)):
            shutil.rmtree(os.path.join(UPLOAD_FOLDER, unique_id))
        raise e  # rethrow for the error handler to handle it


# Have to specify each page manually since static_url_path at line 17
# intercepts the requests if @app.route('/<path:path>') is used.
@app.route('/')
@app.route('/admin', strict_slashes=False)  # trailing dash is optional
@app.route('/manual-conversion', strict_slashes=False)
def serve() -> Response:
    """Serve pages that don't need authentication"""
    return app.send_static_file('index.html')


# Handle endpoint errors
@app.errorhandler(ClientException)
def handle_client_error(error) -> tuple[str, int]:
    """Handle errors caused by the client, like invalid file ids."""
    # TODO LOG client caused errors
    print(error)
    return error.to_response()


@app.errorhandler(Exception)
def handle_server_error(error) -> tuple[str, int] | HTTPException:
    """Handle all other errors."""
    if isinstance(error, HTTPException):
        # Return HTTP errors as is like 404 Not Found
        return error
    # TODO LOG server caused errors
    print(error)
    return 'Internal Server Error', 500


if __name__ == '__main__':
    app.run()
