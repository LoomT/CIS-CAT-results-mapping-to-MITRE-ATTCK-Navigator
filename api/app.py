import io
import json
import os
import shutil
import uuid
from functools import wraps

try:
    from convert import convert_cis_to_attack, combine_results
    from utils import find_file, ClientException
    from db.db import initialize_db
    from db.db_methods import get_metadata
    from db.db_utils import extract_metadata
except ImportError:
    from .convert import convert_cis_to_attack, combine_results
    from .utils import find_file, ClientException
    from .db.db import initialize_db
    from .db.db_methods import get_metadata
    from .db.db_utils import extract_metadata


from flask import Flask, request, send_file, Response, g
from flask.cli import load_dotenv
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException


load_dotenv()


def create_app(config=None):
    """Application factory pattern"""
    app = Flask(__name__, static_folder=os.getenv('FLASK_STATIC_FOLDER'),
                static_url_path='/')

    # Default configuration
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')

    # Apply any additional configuration
    if config:
        app.config.update(config)

    # Ensure upload folder exists
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Initialize database
    db = initialize_db(app)
    app.db = db  # Store db instance on app for easy access

    # Register routes
    register_routes(app)
    register_error_handlers(app)

    return app


def register_routes(app):
    """Register all routes with the app"""
    upload_folder = app.config['UPLOAD_FOLDER']
    db = app.db

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
            g.is_department_admin = get_user_department(g.current_user) \
                is not None
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
            if g.is_super_admin or can_access_department(g.current_user,
                                                         dept_id):
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
        """Delete a department and all its user assignments
        (super admin only)"""
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
            if g.is_super_admin or can_access_department(g.current_user,
                                                         dept_id):
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
            return {'message':
                    'Department ID and user handle are required'}, 400

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
                'message':
                f'User is already assigned to department: {dept_name}'
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
            return {'message':
                    'Department ID and user handle are required'}, 400

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

    @app.get("/api/files/<file_id>")
    def get_converted_file(file_id: str) -> tuple[str, int] | Response:
        """Endpoint for retrieving a file by its unique id."""
        file_name, file_path = find_file(upload_folder, file_id)

        with open(file_path, 'r', encoding='utf-8') as F:
            cis_data = json.load(F)

        attack_data = convert_cis_to_attack(cis_data)

        mem = io.BytesIO(json.dumps(attack_data).encode('utf-8'))

        return send_file(
            mem,
            as_attachment=True,
            download_name=f'converted_{file_name}'
        )

    @app.get('/api/files', strict_slashes=False)
    def get_files_metadata() -> tuple[str, int] | dict:
        """
        Endpoint for retrieving a list of all stored files' Metadata.
        Endpoint supports filtering by various parameters
        (check on execute_query for more information).
        Supports pagination with page and page_size parameters.
        page is the page number to retrieve, starting from 0, and
        page_size is the number of items per page, default is 20.
        """

        # query Metadata objects from the database based on request arguments
        try:
            return get_metadata(request.args)
        except Exception as e:
            print(f"Failed fetching metadata: {e}")
            return "Internal server error", 500

    @app.get('/api/files/aggregate')
    def aggregate_and_convert_files() -> tuple[str, int] | Response:
        """
        Endpoint for combining and retrieving multiple files
        by their unique ids. Can also be queryed with the same parameters
        as /api/files to combine all the files it returns.
        """
        file_ids = request.args.getlist('id')

        # If no file ids are provided, try the request arguments
        # if no IDs, then return 400 Bad Request
        if not file_ids:
            file_ids = get_metadata(request.args, ids=True)
            if not file_ids:
                return "No file ids were found " \
                       "matching the query constraints", 404

        cis_data_list = []

        for file_id in file_ids:
            _, file_path = find_file(upload_folder, file_id)

            with open(file_path, 'r', encoding='utf-8') as F:
                cis_data_list.append(json.load(F))

        attack_data = combine_results(cis_data_list)

        mem = io.BytesIO(json.dumps(attack_data).encode('utf-8'))

        return send_file(
            mem,
            as_attachment=True,
            download_name='converted_aggregated_results.json'
        )

    @app.post('/api/files/')
    def save_file() -> tuple[str, int] | tuple[dict[str, str], int]:
        """Endpoint for uploading, converting and storing the converted file.
        Returns a response with the unique id of the converted file."""
        unique_id = str(uuid.uuid4())
        try:
            if 'file' not in request.files:
                return "No file part", 400

            file = request.files['file']
            if file.filename == '':
                return "No selected file", 400

            # Secure the filename to be able to safely store it
            filename = secure_filename(file.filename)

            # Secure filename might become empty
            if filename == '':
                return "Invalid filename", 400

            # Avoid collisions with existing files
            while os.path.exists(os.path.join(upload_folder, unique_id)):
                unique_id = str(uuid.uuid4())

            # Create a unique directory
            os.makedirs(os.path.join(upload_folder, unique_id))

            # Process the file (modify as needed)
            file_path = os.path.join(
                upload_folder, unique_id, filename
            )

            # DATABASE PART #
            try:
                metadata = extract_metadata(filename)
                # Set remaining metadata fields
                metadata.id = unique_id
                metadata.ip_address = request.remote_addr
                metadata.filename = filename

                db.session.add(metadata)
                db.session.commit()
                db.session.refresh(metadata)
            except Exception as e:
                print(f"Error extracting metadata: {e}")
                db.session.rollback()
                return "Error saving file metadata", 500

            # END OF DATABASE PART #

            try:
                cis_data = json.load(file.stream)
            except json.JSONDecodeError:
                return "Invalid file format", 400

            with open(file_path, 'w', encoding='utf-8') as F:
                json.dump(cis_data, F, ensure_ascii=False, indent=2)

            # Send the id of the modified file back to the client
            # TODO: change return to return Metadata object
            return {
                'id': unique_id,
                'filename': filename,
            }, 201

        except Exception as e:
            # Clean up on error, remove the directory with all its files
            if os.path.exists(os.path.join(upload_folder, unique_id)):
                shutil.rmtree(os.path.join(upload_folder, unique_id))
            raise e  # rethrow for the error handler to handle it

    # Have to specify each page manually since static_url_path at line 17
    # intercepts the requests if @app.route('/<path:path>') is used.
    @app.route('/')
    @app.route('/admin', strict_slashes=False)  # trailing dash is optional
    @app.route('/manual-conversion', strict_slashes=False)
    def serve() -> Response:
        """Serve pages that don't need authentication"""
        return app.send_static_file('index.html')


def register_error_handlers(app):
    """Register error handlers with the app"""
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


app = create_app()


if __name__ == '__main__':
    app.run()
