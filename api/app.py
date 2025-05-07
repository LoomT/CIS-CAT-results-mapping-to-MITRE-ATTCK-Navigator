import os
import shutil
import time
import uuid

from flask import (Flask, send_from_directory, request, send_file,
                   Response)
from flask.cli import load_dotenv
from werkzeug.utils import secure_filename

load_dotenv()
app = Flask(__name__, static_folder=os.getenv('FLASK_STATIC_FOLDER'),
            static_url_path='/')

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/api/time')
def get_current_time():
    return {'time': time.time()}


@app.get("/api/files/<file_id>")
def get_file(file_id: str) -> tuple[str, int] | Response:
    """Endpoint for retrieving a file by its unique id."""
    try:
        file_dir = os.path.join(UPLOAD_FOLDER, file_id)
        # Check if a folder with the id exists
        if os.path.isdir(file_dir):
            # The folder should contain exactly one file
            files = os.listdir(file_dir)
            if len(files) == 1:
                return send_file(
                    os.path.join(file_dir, files[0]),
                    as_attachment=True,
                    download_name=files[0]
                )

            # Should not happen
            elif len(files) > 1:
                return "Multiple files found", 500
            else:
                return "No file found", 500
        else:
            return "No file by this id found", 404
    except Exception as e:
        return str(e), 500


@app.post('/api/files')
def convert_and_save_file() -> tuple[str, int] | tuple[dict[str, str], int]:
    """Endpoint for uploading, converting and storing the converted file.
    Returns a response with the unique id of the converted file."""
    unique_id = str(uuid.uuid4())
    try:
        if 'file' not in request.files:
            return 'No file part', 400

        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400

        if file:
            # Secure the filename to be able to safely store it
            filename = secure_filename(file.filename)

            # Secure filename might become empty
            if filename == '':
                return 'Invalid filename', 400

            file_path = os.path.join(UPLOAD_FOLDER, unique_id, filename)

            # Create a unique directory
            os.makedirs(os.path.join(UPLOAD_FOLDER, unique_id))

            # Save the uploaded file
            file.save(file_path)

            # TODO assert that the file is of correct format

            # Process the file (modify as needed)
            modified_filename = f"converted_{filename}"
            modified_file_path = os.path.join(
                UPLOAD_FOLDER, unique_id, modified_filename
            )

            # Example modification: create a copy with modified_ prefix
            with open(file_path, 'rb') as f:
                content = f.read()

            # Save modified content
            with open(modified_file_path, 'wb') as f:
                f.write(content)

            os.remove(file_path)

            # Send the id of the modified file back to the client
            return {
                'id': unique_id,
                'filename': modified_filename,
            }, 201

        return 'File upload failed', 400

    except Exception as e:
        # Clean up on error, remove the directory with all its files
        if os.path.exists(os.path.join(UPLOAD_FOLDER, unique_id)):
            shutil.rmtree(os.path.join(UPLOAD_FOLDER, unique_id))
        return str(e), 500


# Serve React App
@app.route('/')
def serve() -> Response:
    print('connecting')
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run()
