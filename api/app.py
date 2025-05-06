import os
import threading
import time

from flask import (Flask, send_from_directory, request, send_file,
                   make_response)
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


def cleanup_files(file_paths):
    """Clean up temporary files after the response has been sent"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up file {file_path}: {e}")


@app.post('/api/files')
def convert_file():
    """Endpoint for uploading, converting
    and sending a file back to the client"""
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    if file:
        # Secure the filename
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        modified_file_path = None

        try:
            # Save the uploaded file
            file.save(file_path)

            # Process the file (modify as needed)
            modified_filename = f"modified_{filename}"
            modified_file_path = os.path.join(UPLOAD_FOLDER, modified_filename)

            # Example modification: create a copy with modified_ prefix
            with open(file_path, 'rb') as f:
                content = f.read()

            # Save modified content
            with open(modified_file_path, 'wb') as f:
                f.write(content)

            # Send the modified file back to client
            response = make_response(send_file(
                modified_file_path,
                as_attachment=True,
                download_name=modified_filename
            ))

            # Add the modified filename to headers
            response.headers['X-Modified-Filename'] = modified_filename

            # for now delete the files
            threading.Timer(3.0, cleanup_files,
                            args=[[file_path, modified_file_path]]).start()

            return response

        except Exception as e:
            # Clean up on error
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(modified_file_path):
                os.remove(modified_file_path)
            return str(e), 500

    return 'File upload failed', 400


# Serve React App
@app.route('/')
def serve():
    print('connecting')
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run()
