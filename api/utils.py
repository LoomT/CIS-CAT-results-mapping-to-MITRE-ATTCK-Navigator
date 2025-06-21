import os

from werkzeug.utils import secure_filename


class ClientException(Exception):
    """Custom exception for client errors
     with message and status code to be returned in the response."""

    def __init__(self, message: str, status_code: int) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def to_response(self) -> tuple[dict, int]:
        """Convert exception to a Flask response tuple."""
        return {'message': self.message}, self.status_code


def find_file(upload_folder: str, file_id: str) -> tuple[str, str]:
    """Find a file by its unique id in the Uploads folder.
    :returns: Filename and path to the file tuple."""
    # UUIDs are not case-sensitive
    file_id = file_id.lower()
    # Ensure file_id is safe to use as a filename
    secure_file_id = secure_filename(file_id)
    if secure_file_id != file_id:
        raise ClientException("Invalid file id", 400)

    file_dir = os.path.join(upload_folder, file_id)
    # Check if a folder with the id exists
    if not os.path.isdir(file_dir):
        raise ClientException("No file by this id found", 404)

    # The folder should contain exactly one file
    files = os.listdir(file_dir)

    # Should not happen
    if len(files) > 1:
        raise ClientException("Multiple files found", 500)
    elif len(files) == 0:
        raise ClientException("No file found", 500)

    return files[0], os.path.join(file_dir, files[0])


def validate_user_json(data: dict) -> None:
    """
    Validates the JSON payload for user creation or deletion requests.

    :param data: The incoming HTTP request JSON object
    :raises ClientException
    :return: None
    """
    if (
        not data
        or data.get('department_id') is None
        or not data.get('user_handle')
        or not data.get('user_handle').strip()
    ):
        raise ClientException(
            "Department ID and user handle are required",
            400
        )

    if not isinstance(data['department_id'], int):
        raise ClientException(
            "Department ID must be an integer",
            400
        )
