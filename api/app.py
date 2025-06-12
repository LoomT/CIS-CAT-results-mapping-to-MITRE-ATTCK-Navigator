import io
import json
import os
import shutil
import uuid

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


from flask import (Flask, request, send_file, Response)


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

            try:
                cis_data = json.load(file.stream)
            except json.JSONDecodeError:
                return "Invalid file format", 400

            with open(file_path, 'w', encoding='utf-8') as F:
                json.dump(cis_data, F, ensure_ascii=False, indent=2)

            # DATABASE PART #
            try:
                bench_type = (cis_data.get('benchmark-title')
                              .replace(' ', '_'))
                metadata = extract_metadata(filename, bench_type)
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
        return "Internal Server Error", 500


app = create_app()


if __name__ == '__main__':
    app.run()
