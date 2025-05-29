import json
import os


def test_convert_file_success(client, uploads_folder, mocker):
    """Test case for successful file conversion."""
    os.makedirs(f'{uploads_folder}/test-file-id', exist_ok=True)
    with open(f'{uploads_folder}/test-file-id/test.json', 'w') as fs:
        json.dump({'mock': 'data'}, fs)

    mock_convert = mocker.patch('api.app.convert_cis_to_attack')
    mock_convert.return_value = {'converted': 'data'}

    response = client.get('/api/files/test-file-id')

    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    assert response.data == json.dumps({'converted': 'data'}).encode('utf-8')

    mock_convert.assert_called_once_with({'mock': 'data'})


def test_convert_file_invalid_file_id(client):
    """Test case where an invalid file ID is provided."""

    response = client.get('/api/files/%5c')

    assert response.status_code == 400
    assert response.data.decode('utf-8') == "Invalid file id"


def test_convert_file_file_not_found(client):
    """Test case for non-existing file."""

    response = client.get('/api/files/non-existing-id')

    assert response.status_code == 404
    assert response.data.decode('utf-8') == "No file by this id found"


def test_convert_file_multiple_files_found(client, uploads_folder):
    """Test case for a folder with multiple files."""
    os.makedirs(f'{uploads_folder}/multiple-files-id', exist_ok=True)
    with open(f'{uploads_folder}/multiple-files-id/file1.json', 'w') as fs:
        json.dump({'mock': 'data'}, fs)

    with open(f'{uploads_folder}/multiple-files-id/file2.json', 'w') as fs:
        json.dump({'mock': 'data'}, fs)

    response = client.get('/api/files/multiple-files-id')

    assert response.status_code == 500
    assert response.data.decode('utf-8') == "Multiple files found"


def test_convert_file_unexpected_error(client, mocker):
    """Test case for an unexpected server error."""
    mocker.patch('api.app.find_file',
                 side_effect=Exception("Unexpected server error"))

    response = client.get('/api/files/unexpected-error-id')

    assert response.status_code == 500
    assert "Unexpected error while getting file" in response.data.decode(
        'utf-8')
