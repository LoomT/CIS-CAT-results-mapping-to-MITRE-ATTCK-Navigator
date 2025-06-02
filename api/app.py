import io
import json
import os
import shutil
import uuid

try:
    from convert import convert_cis_to_attack, combine_results
    from utils import find_file, ClientException
except ImportError:
    from .convert import convert_cis_to_attack, combine_results
    from .utils import find_file, ClientException

from flask import (Flask, request, send_file, Response)
from flask.cli import load_dotenv
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException

load_dotenv()
app = Flask(__name__, static_folder=os.getenv('FLASK_STATIC_FOLDER'),
            static_url_path='/')

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.get("/api/files/<file_id>")
def convert_file(file_id: str) -> tuple[str, int] | Response:
    """Endpoint for retrieving a file by its unique id."""
    file_name, file_path = find_file(UPLOAD_FOLDER, file_id)

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
def get_files() -> (
        tuple[dict[str, list[dict]], int] | tuple[str, int] | Response
):
    """Middleware for determining whether to return queried files' metadata
    or to aggregate and convert multiple files."""
    if request.args.get('aggregate', 'false').lower() == 'true':
        return aggregate_and_convert_files()
    else:
        return get_files_metadata()


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
                files_list.append({
                    'id': file_id,
                    'filename': dir_files[0]
                })
            # TODO else fail?

    return {'files': files_list}, 200


def aggregate_and_convert_files() -> tuple[str, int] | Response:
    """Endpoint for combining and retrieving multiple files
     by their unique ids."""
    file_ids = request.args.getlist('id')

    if not file_ids:
        return "No file ids provided", 400

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
        while os.path.exists(os.path.join(UPLOAD_FOLDER, unique_id)):
            unique_id = str(uuid.uuid4())

        # Create a unique directory
        os.makedirs(os.path.join(UPLOAD_FOLDER, unique_id))

        file_path = os.path.join(
            UPLOAD_FOLDER, unique_id, filename
        )

        try:
            cis_data = json.load(file.stream)
        except json.JSONDecodeError:
            return "Invalid file format", 400

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
    return "Internal Server Error", 500


if __name__ == '__main__':
    app.run()
