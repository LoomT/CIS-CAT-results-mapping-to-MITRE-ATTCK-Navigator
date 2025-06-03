import json
import os
import shutil
import uuid

try:
    from convert import convert_cis_to_attack
except ImportError:
    from .convert import convert_cis_to_attack


from flask import (Flask, request, send_file, Response)
from flask.cli import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()
app = Flask(__name__, static_folder=os.getenv('FLASK_STATIC_FOLDER'),
            static_url_path='/')

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.get("/api/files/<file_id>")
def get_file(file_id: str) -> tuple[str, int] | Response:
    """Endpoint for retrieving a file by its unique id."""
    try:
        # Ensure file_id is safe to use as a filename
        secure_file_id = secure_filename(file_id)
        if secure_file_id != file_id:
            return "Invalid file id", 400

        file_dir = os.path.join(UPLOAD_FOLDER, file_id)
        # Check if a folder with the id exists
        if not os.path.isdir(file_dir):
            return "No file by this id found", 404

        # The folder should contain exactly one file
        files = os.listdir(file_dir)

        # Should not happen
        if len(files) > 1:
            return "Multiple files found", 500
        elif len(files) == 0:
            return "No file found", 500

        return send_file(
            os.path.join(file_dir, files[0]),
            as_attachment=True,
            download_name=files[0]
        )

    except Exception as e:
        # TODO configure logging in the future
        print(f"Unexpected error while getting file: {e}")
        return "Unexpected error while getting file", 500


@app.post('/api/files/')
def convert_and_save_file() -> tuple[str, int] | tuple[dict[str, str], int]:
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

        # Process the file (modify as needed)
        modified_filename = f'converted_{filename}'
        modified_file_path = os.path.join(
            UPLOAD_FOLDER, unique_id, modified_filename
        )

        try:
            cis_data = json.load(file.stream)
        except json.JSONDecodeError:
            return "Invalid file format", 400

        attck_data = convert_cis_to_attack(cis_data)
        with open(modified_file_path, 'w', encoding='utf-8') as F:
            json.dump(attck_data, F, ensure_ascii=False, indent=2)

        # Send the id of the modified file back to the client
        return {
            'id': unique_id,
            'filename': modified_filename,
        }, 201

    except Exception as e:
        # Clean up on error, remove the directory with all its files
        if os.path.exists(os.path.join(UPLOAD_FOLDER, unique_id)):
            shutil.rmtree(os.path.join(UPLOAD_FOLDER, unique_id))
        # TODO configure logging in the future
        print(f"Unexpected error while processing file: {e}")
        return "Unexpected error while processing file", 500


# Have to specify each page manually since static_url_path at line 17
# intercepts the requests if @app.route('/<path:path>') is used.
@app.route('/')
@app.route('/admin', strict_slashes=False)  # trailing dash is optional
@app.route('/manual-conversion', strict_slashes=False)
def serve() -> Response:
    """Serve pages that don't need authentication"""
    return app.send_static_file('index.html')


if __name__ == '__main__':
    app.run()
