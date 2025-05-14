import os
import shutil
import uuid
from .convert import convert_cis_to_attack

from flask import (Flask, send_from_directory, request, send_file, Response)
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


@app.post('/api/files')
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
        original_file_path = os.path.join(
            UPLOAD_FOLDER, unique_id, filename
        )
        file.save(original_file_path)
        convert_cis_to_attack(original_file_path, modified_file_path)

        # Cleanup
        os.remove(original_file_path)
        # TODO assert that the file is of correct format

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


def cleanup_files(file_paths):
    """Clean up temporary files after the response has been sent"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up file {file_path}: {e}")


# Serve React App
@app.route('/')
def serve() -> Response:
    print('connecting')
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run()
