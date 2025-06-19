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
    from db.db_methods import get_metadata, get_user_departments, \
        get_all_departments_with_access, get_department_by_name, \
        create_department, delete_department, \
        get_all_users_with_departments, get_department, \
        add_user_to_department, remove_user_from_department, \
        get_bearer_token_by_token, update_bearer_token_last_used, \
        create_bearer_token, verify_bearer_token_access, \
        revoke_bearer_token, get_bearer_tokens_for_departments
    from db.db_utils import extract_metadata
except ImportError:
    from .convert import convert_cis_to_attack, combine_results
    from .utils import find_file, ClientException
    from .db.db import initialize_db
    from .db.db_methods import get_metadata, get_user_departments, \
        get_all_departments_with_access, get_department_by_name, \
        create_department, delete_department, \
        get_all_users_with_departments, get_department, \
        add_user_to_department, remove_user_from_department, \
        get_bearer_token_by_token, update_bearer_token_last_used, \
        create_bearer_token, verify_bearer_token_access, \
        revoke_bearer_token, get_bearer_tokens_for_departments
    from .db.db_utils import extract_metadata


from flask import Flask, request, send_file, Response, g
from flask.cli import load_dotenv
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException


def create_app(config=None):
    """Application factory pattern"""
    load_dotenv()

    app = Flask(__name__, static_folder=os.getenv('FLASK_STATIC_FOLDER'),
                static_url_path='/')

    # Default configuration
    app.config['ENABLE_SSO'] = os.getenv('ENABLE_SSO', 'False').strip() \
        .lower() in {'1', 'true', 't', 'yes', 'y', 'on'}
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
    app.config['SUPER_ADMINS'] = set()

    # Parse super admins from environment variable
    super_admin_env = os.getenv('SUPER_ADMINS', "")
    if super_admin_env:
        app.config['SUPER_ADMINS'] = set(
            handle.strip()
            for handle in super_admin_env.split(';')
            if handle.strip()
        )

    app.config['TRUSTED_IPS'] = set()

    # Parse trusted IP addresses from environment variable
    trusted_ips_env = os.getenv('TRUSTED_IPS', "")
    if trusted_ips_env:
        app.config['TRUSTED_IPS'] = set(
            ip.strip()
            for ip in trusted_ips_env.split(';')
            if ip.strip()
        )

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

    @app.before_request
    def before_request():
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token_str = auth_header[7:]  # Remove 'Bearer ' prefix
            token = get_bearer_token_by_token(token_str)

            if token:
                # Update last used timestamp
                update_bearer_token_last_used(token)

                # Set context for bearer token authentication
                g.current_user = token.machine_name
                g.is_super_admin = False
                g.is_department_admin = False
                g.is_bearer_token = True
                g.bearer_token = token
                g.department_id = token.department_id
                return

        # If no bearer token, proceed with SSO or default authentication
        if app.config['ENABLE_SSO']:
            # Get the client's IP address
            # Check X-Forwarded-For header first for caddy
            if request.headers.get('X-Forwarded-For'):
                # X-Forwarded-For can contain multiple IPs, get the first one
                client_ip = request.headers.get('X-Forwarded-For') \
                    .split(',')[0].strip()
            else:
                client_ip = request.remote_addr

            is_trusted_ip = client_ip in app.config['TRUSTED_IPS']

            # Parse X-Forwarded-User header
            user_handle = request.headers.get('X-Forwarded-User')
            if is_trusted_ip and user_handle:
                g.current_user = user_handle.strip()
                g.is_super_admin = g.current_user in app.config['SUPER_ADMINS']
                g.is_department_admin = len(get_all_departments_with_access(
                    g.current_user, g.is_super_admin)) > 0
                g.is_bearer_token = False
            else:
                g.current_user = None
                g.is_super_admin = False
                g.is_department_admin = False
                g.is_bearer_token = False
        else:
            # SSO disabled - default admin access (unless using bearer token)
            g.current_user = "admin"
            g.is_super_admin = True
            g.is_department_admin = True
            g.is_bearer_token = False

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

    def require_auth(f):
        """
        Decorator to require admin privileges
        (super admin or department admin) or bearer token authentication
        """

        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.get('current_user'):
                return {'message': 'Authentication required'}, 401
            if not (g.get('is_super_admin') or g.get('is_department_admin')
                    or g.get('is_bearer_token')):
                return {'message': 'Admin privileges required'}, 403
            return f(*args, **kwargs)

        return decorated_function

    @app.get('/api/admin/bearer-tokens')
    @require_admin
    def api_get_bearer_tokens():
        """Get all bearer tokens for departments the user has access to."""
        try:
            # Get accessible departments
            departments = get_all_departments_with_access(
                g.current_user,
                g.is_super_admin
            )
            department_ids = [dept.id for dept in departments]

            # Get tokens for these departments
            tokens = get_bearer_tokens_for_departments(department_ids)

            return {
                'tokens': [
                    {
                        'id': token.id,
                        'machine_name': token.machine_name,
                        'department_id': token.department_id,
                        'department_name': token.department.name,
                        'created_at': token.created_at.isoformat(),
                        'last_used': token.last_used.isoformat()
                        if token.last_used else None,
                        'created_by': token.created_by,
                        'is_active': token.is_active
                    }
                    for token in tokens
                ],
                'departments': [
                    {
                        'id': dept.id,
                        'name': dept.name
                    }
                    for dept in departments
                ]
            }, 200
        except Exception as e:
            print(f"Error fetching bearer tokens: {e}")
            return {'message': 'Error fetching bearer tokens'}, 500

    @app.post('/api/admin/bearer-tokens')
    @require_admin
    def api_create_bearer_token():
        """Create a new bearer token for a department."""
        data = request.get_json()

        if not data or not data.get('department_id') \
                or not data.get('machine_name'):
            return {
                'message': 'Department ID and machine name are required'
            }, 400

        try:
            dept_id = int(data['department_id'])
            machine_name = data['machine_name'].strip()

            # Verify user has access to this department
            departments = get_all_departments_with_access(
                g.current_user,
                g.is_super_admin
            )
            department_ids = [dept.id for dept in departments]

            if dept_id not in department_ids:
                return {
                    'message': 'You do not have access to this department'
                }, 403

            # Create the token
            token = create_bearer_token(
                department_id=dept_id,
                machine_name=machine_name,
                created_by=g.current_user
            )

            # Return the token data INCLUDING the actual token
            # This is the only time we'll show the full token
            return {
                'token': token.to_dict_with_token()
            }, 201

        except ValueError:
            return {'message': 'Invalid department ID'}, 400
        except Exception as e:
            print(f"Error creating bearer token: {e}")
            db.session.rollback()
            return {'message': 'Error creating bearer token'}, 500

    @app.delete('/api/admin/bearer-tokens/<int:token_id>')
    @require_admin
    def api_revoke_bearer_token(token_id):
        """Revoke a bearer token."""
        try:
            # Verify user has access to this token's department
            departments = get_all_departments_with_access(
                g.current_user,
                g.is_super_admin
            )
            department_ids = [dept.id for dept in departments]

            if not verify_bearer_token_access(token_id, department_ids):
                return {'message': 'You do not have access to this token'}, 403

            if revoke_bearer_token(token_id):
                return {'message': 'Token revoked successfully'}, 200
            else:
                return {'message': 'Token not found'}, 404

        except Exception as e:
            print(f"Error revoking bearer token: {e}")
            db.session.rollback()
            return {'message': 'Error revoking bearer token'}, 500

    @app.get('/api/admin/departments')
    @require_admin
    def api_get_departments():
        """
        Get all departments (super admins see all,
        dept admins see only theirs)
        """
        try:
            departments = get_all_departments_with_access(
                g.current_user,
                g.is_super_admin
            )

            return {
                'departments': [
                    {
                        'id': dept.id,
                        'name': dept.name,
                    }
                    for dept in departments
                ]
            }, 200
        except Exception as e:
            print(f"Error fetching departments: {e}")
            return {'message': 'Error fetching departments'}, 500

    @app.post('/api/admin/departments')
    @require_super_admin
    def api_create_department():
        """Create a new department (super admin only)"""
        data = request.get_json()

        if not data or not data.get('name'):
            return {'message': 'Department name is required'}, 400

        dept_name = data['name'].strip()

        try:
            # Check if department name already exists
            existing_dept = get_department_by_name(dept_name)
            if existing_dept:
                return {'message': 'Department name already exists'}, 400

            # Create new department
            department = create_department(dept_name)

            return {
                'department': {
                    'id': department.id,
                    'name': department.name,
                }
            }, 201
        except Exception as e:
            print(f"Error creating department: {e}")
            db.session.rollback()
            return {'message': 'Error creating department'}, 500

    @app.delete('/api/admin/departments/<int:department_id>')
    @require_super_admin
    def api_delete_department(department_id):
        """Delete a department and all its user assignments
        (super admin only)"""
        try:
            if delete_department(department_id):
                return {'message': 'Department deleted successfully'}, 200
            else:
                return {'message': 'Department not found'}, 404
        except Exception as e:
            print(f"Error deleting department: {e}")
            db.session.rollback()
            return {'message': 'Error deleting department'}, 500

    @app.get('/api/admin/users')
    @require_super_admin
    def api_get_users():
        """Get all users and their department assignments"""
        try:
            users = get_all_users_with_departments()
            return {'users': users}, 200
        except Exception as e:
            print(f"Error fetching users: {e}")
            return {'message': 'Error fetching users'}, 500

    @app.post('/api/admin/department-users')
    @require_super_admin
    def api_add_user_to_department():
        """Add a user to a department (super admin only)"""
        data = request.get_json()

        if (
            not data
            or not data.get('department_id')
            or not data.get('user_handle')
        ):
            return {'message':
                    'Department ID and user handle are required'}, 400

        try:
            dept_id = int(data['department_id'])
            user_handle = data['user_handle'].strip()

            # Validate department exists
            department = get_department(dept_id)
            if not department:
                return {'message': 'Department not found'}, 404

            # Check if user is already in any department
            deps = get_user_departments(user_handle)
            if any([dep.id == dept_id for dep in deps]):
                return {
                    'message':
                    'User is already assigned to this department'
                }, 400

            # Add user to department
            add_user_to_department(dept_id, user_handle)

            return {'message': 'User added to department successfully'}, 201
        except ValueError:
            return {'message': 'Invalid department ID'}, 400
        except Exception as e:
            print(f"Error adding user to department: {e}")
            db.session.rollback()
            return {'message': 'Error adding user to department'}, 500

    @app.delete('/api/admin/department-users')
    @require_super_admin
    def api_remove_user_from_department():
        """Remove a user from a department (super admin only)"""
        data = request.get_json()

        if (
            not data
            or not data.get('department_id')
            or not data.get('user_handle')
        ):
            return {'message':
                    'Department ID and user handle are required'}, 400

        try:
            dept_id = int(data['department_id'])
            user_handle = data['user_handle'].strip()

            # Validate department exists
            department = get_department(dept_id)
            if not department:
                return {'message': 'Department not found'}, 404

            # Remove user from department
            if remove_user_from_department(dept_id, user_handle):
                return {
                    'message': 'User removed from department successfully'
                }, 200
            else:
                return {'message': 'User not found in department'}, 404

        except ValueError:
            return {'message': 'Invalid department ID'}, 400
        except Exception as e:
            print(f"Error removing user from department: {e}")
            db.session.rollback()
            return {'message': 'Error removing user from department'}, 500

    @app.get('/api/auth/status')
    def get_auth_status():
        """Get current user's authentication status"""
        return {
            'user': g.get('current_user'),
            'is_super_admin': g.get('is_super_admin', False),
            'is_department_admin': g.get('is_department_admin', False),
        }, 200

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
    @require_admin
    def get_files_metadata() -> tuple[str | dict, int]:
        """
        Endpoint for retrieving a list of all stored files' Metadata.
        Endpoint supports filtering by various parameters
        (check on execute_query for more information).
        Supports pagination with page and page_size parameters.
        page is the page number to retrieve, starting from 0, and
        page_size is the number of items per page, default is 20.

        If the `verbose` query parameter is set to true, then the response
        will return full file metadata instead of only the ids.
        """

        # query Metadata objects from the database based on request arguments
        try:
            if request.args.get('verbose', 'false') == 'true':
                return get_metadata(
                    g.get('current_user'),
                    g.get('is_super_admin', False),
                    request.args,
                    False
                ), 200
            else:
                ids = get_metadata(
                        g.get('current_user'),
                        g.get('is_super_admin', False),
                        request.args,
                        True
                )
                return {'ids': ids}, 200

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
            file_ids = get_metadata(g.get('current_user'),
                                    g.get('is_super_admin', False),
                                    request.args, ids=True)
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
    @require_auth
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

            department_id = request.args.get('department_id', type=int)

            # Secure the filename to be able to safely store it
            filename = secure_filename(file.filename)

            # Secure filename might become empty
            if filename == '':
                return "Invalid filename", 400

            # Avoid collisions with existing files
            while os.path.exists(os.path.join(upload_folder, unique_id)):
                unique_id = str(uuid.uuid4())

            try:
                cis_data = json.load(file.stream)
            except json.JSONDecodeError:
                return "Invalid file format", 400

            # DATABASE PART #
            try:
                bench_type = (cis_data.get('benchmark-title')
                              .replace(' ', '_'))
                metadata = extract_metadata(filename, bench_type)
                # Set remaining metadata fields
                metadata.id = unique_id
                metadata.ip_address = request.remote_addr
                metadata.filename = filename
                # Handle department assignment

                if hasattr(g, 'is_bearer_token') and g.is_bearer_token:
                    metadata.department_id = g.department_id
                elif department_id:
                    # Verify user has access to this department
                    departments = get_all_departments_with_access(
                        g.current_user,
                        g.is_super_admin
                    )
                    department_ids = [dept.id for dept in departments]

                    if department_id not in department_ids:
                        return {
                            'message': 'You do not have access '
                            'to this department'
                        }, 403

                    metadata.department_id = department_id
                else:
                    return {
                        'message': 'No department supplied'
                    }, 403

                # Only when everything has finished we create the file
                # Its removed on Exception by the upper handler
                # Create a unique directory
                os.makedirs(os.path.join(upload_folder, unique_id))

                file_path = os.path.join(
                    upload_folder, unique_id, filename
                )

                with open(file_path, 'w', encoding='utf-8') as F:
                    json.dump(cis_data, F, ensure_ascii=False, indent=2)

                db.session.add(metadata)
                db.session.commit()
                db.session.refresh(metadata)
            except Exception as e:
                print(f"Error extracting metadata: {e}")
                db.session.rollback()
                raise e

            # END OF DATABASE PART #

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
    @app.route('/manual-upload', strict_slashes=False)
    def serve() -> Response:
        """Serve pages that don't need authentication"""
        return app.send_static_file('index.html')

    @app.route('/admin', strict_slashes=False)
    @require_admin
    def serve_admin() -> Response:
        """Serve pages that need at least admin role"""
        return app.send_static_file('index.html')

    @app.route('/admin/user-management', strict_slashes=False)
    @require_super_admin
    def serve_super_admin() -> Response:
        """Serve pages that need super admin role"""
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
