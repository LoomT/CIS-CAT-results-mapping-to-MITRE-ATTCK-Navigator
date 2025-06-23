import json
import os
import pytest
from unittest.mock import mock_open


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


@pytest.mark.parametrize("file_id",
                         ['file%20id', '%5c', 'file\\id']
                         )
def test_convert_file_invalid_file_id(client, file_id):
    """Test case where an invalid file ID is provided."""

    response = client.get(f'/api/files/{file_id}')

    assert response.status_code == 400
    assert response.get_json() == {'message': 'Invalid file id'}


def test_convert_file_file_not_found(client):
    """Test case for non-existing file."""

    response = client.get('/api/files/non-existing-id')

    assert response.status_code == 404
    assert response.get_json() == {'message': 'No file by this id found'}


def test_convert_file_multiple_files_found(client, uploads_folder):
    """Test case for a folder with multiple files."""
    os.makedirs(f'{uploads_folder}/multiple-files-id', exist_ok=True)
    with open(f'{uploads_folder}/multiple-files-id/file1.json', 'w') as fs:
        json.dump({'mock': 'data'}, fs)

    with open(f'{uploads_folder}/multiple-files-id/file2.json', 'w') as fs:
        json.dump({'mock': 'data'}, fs)

    response = client.get('/api/files/multiple-files-id')

    assert response.status_code == 500
    assert response.get_json() == {'message': 'Multiple files found'}


def test_convert_file_unexpected_error(client, mocker):
    """Test case for an unexpected server error."""
    mocker.patch('api.app.find_file',
                 side_effect=Exception("Unexpected server error"))

    response = client.get('/api/files/unexpected-error-id')

    assert response.status_code == 500
    assert "Internal Server Error" in response.data.decode(
        'utf-8')


def test_get_converted_file_success(client, bootstrap_full):
    """Test successful file retrieval and conversion"""
    response = client.get('/api/files/file_id1')

    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    assert response.headers['Content-Disposition'] == (
        'attachment; '
        'filename=converted_host-cis_input-20250101T000000Z-NonPassing.json'
    )

    # Verify the response contains JSON data
    response_data = json.loads(response.data)
    assert isinstance(response_data, dict)


def test_get_converted_file_different_files(client, bootstrap_full):
    """Test retrieving different files returns different data"""
    response1 = client.get('/api/files/file_id1')
    response2 = client.get('/api/files/file_id2')

    assert response1.status_code == 200
    assert response2.status_code == 200

    # Both should be successful but may have different content
    data1 = json.loads(response1.data)
    data2 = json.loads(response2.data)

    # Verify they're both valid JSON objects
    assert isinstance(data1, dict)
    assert isinstance(data2, dict)


def test_get_converted_file_invalid_json_in_file(client, bootstrap_full,
                                                 mocker):
    """Test handling of invalid JSON in the file"""
    # Mock open to return invalid JSON
    mock_file_content = "invalid json content"
    mocker.patch('builtins.open', mock_open(read_data=mock_file_content))

    # Also need to mock find_file to avoid file not found error
    mocker.patch('api.app.find_file',
                 return_value=('test.json', '/path/to/test.json'))

    response = client.get('/api/files/file_id1')

    assert response.status_code == 500
    assert "Internal Server Error" in response.data.decode('utf-8')


def test_get_converted_file_conversion_error(client, bootstrap_full, mocker):
    """Test handling of conversion errors"""
    # Mock the conversion function to raise an exception
    mocker.patch('api.app.convert_cis_to_attack',
                 side_effect=Exception("Conversion failed"))

    response = client.get('/api/files/file_id1')

    assert response.status_code == 500
    assert "Internal Server Error" in response.data.decode('utf-8')


def test_get_converted_file_file_read_error(client, bootstrap_full, mocker):
    """Test handling of file read errors"""
    # Mock find_file to return a valid result but open to fail
    mocker.patch('api.app.find_file',
                 return_value=('test.json', '/path/to/test.json'))
    mocker.patch('builtins.open', side_effect=IOError("File read error"))

    response = client.get('/api/files/file_id1')

    assert response.status_code == 500
    assert "Internal Server Error" in response.data.decode('utf-8')


def test_get_converted_file_very_long_id(client, bootstrap_full):
    """Test with very long file ID"""
    long_id = 'a' * 1000
    response = client.get(f'/api/files/{long_id}')

    assert response.status_code == 404
    response_data = response.get_json()
    assert response_data['message'] == 'No file by this id found'


def test_get_converted_file_response_headers(client, bootstrap_full):
    """Test that response headers are set correctly"""
    response = client.get('/api/files/file_id1')

    assert response.status_code == 200
    assert 'Content-Disposition' in response.headers
    assert 'attachment' in response.headers['Content-Disposition']
    assert 'converted_' in response.headers['Content-Disposition']
    assert response.mimetype == 'application/json'


def test_get_converted_file_large_file_handling(client, bootstrap_full,
                                                mocker):
    """Test handling of large files"""
    # Create a large JSON object
    large_data = {"data": ["item"] * 10000}
    large_json = json.dumps(large_data)

    mocker.patch('api.app.find_file',
                 return_value=('large_test.json', '/path/to/large_test.json'))
    mocker.patch('builtins.open', mock_open(read_data=large_json))
    mocker.patch('api.app.convert_cis_to_attack', return_value=large_data)

    response = client.get('/api/files/test_large')

    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert len(response_data['data']) == 10000


def test_get_converted_file_unicode_handling(client, bootstrap_full, mocker):
    """Test handling of Unicode characters in file content"""
    unicode_data = {"message": "Test with unicode: 你好, café, 🚀"}
    unicode_json = json.dumps(unicode_data, ensure_ascii=False)

    mocker.patch('api.app.find_file', return_value=(
        'unicode_test.json', '/path/to/unicode_test.json'
    ))
    mocker.patch('builtins.open', mock_open(read_data=unicode_json))
    mocker.patch('api.app.convert_cis_to_attack', return_value=unicode_data)

    response = client.get('/api/files/test_unicode')

    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data['message'] == "Test with unicode: 你好, café, 🚀"


def test_get_converted_file_method_not_allowed(client, bootstrap_full):
    """Test that other HTTP methods are not allowed"""
    file_id = 'file_id1'

    # POST should not be allowed
    response = client.post(f'/api/files/{file_id}')
    assert response.status_code == 405

    # PUT should not be allowed
    response = client.put(f'/api/files/{file_id}')
    assert response.status_code == 405

    # DELETE should not be allowed
    response = client.delete(f'/api/files/{file_id}')
    assert response.status_code == 405


def test_get_converted_file_case_sensitivity(client, bootstrap_full):
    """
    Test case sensitivity of file IDs
    Paths and UUIDs are not case-sensitive
    """
    response_lower = client.get('/api/files/file_id1')
    response_upper = client.get('/api/files/FILE_ID1')

    assert response_lower.status_code == 200
    assert response_upper.status_code == 200


@pytest.mark.parametrize("file_id,expected_status", [
    ("file_id1", 200),
    ("file_id2", 200),
    ("file_id3", 200),
    ("nonexistent", 404)
])
def test_get_converted_file_parametrized(client, bootstrap_full, file_id,
                                         expected_status):
    """Parametrized test for different file IDs"""
    if file_id == "":
        response = client.get('/api/files/')
    else:
        response = client.get(f'/api/files/{file_id}')

    assert response.status_code == expected_status


def test_get_converted_file_encoding_consistency(client, mocker):
    """Test that UTF-8 encoding is handled consistently"""
    test_data = {"text": "Special chars: àáâãäåæçèéêë"}
    json_data = json.dumps(test_data, ensure_ascii=False)

    mocker.patch('api.app.find_file', return_value=(
        'encoding_test.json', '/path/to/encoding_test.json'
    ))

    # Mock open with UTF-8 encoding
    mock_file = mock_open(read_data=json_data)
    mocker.patch('builtins.open', mock_file)
    mocker.patch('api.app.convert_cis_to_attack', return_value=test_data)

    response = client.get('/api/files/test_encoding')

    assert response.status_code == 200
    # Verify file was opened with UTF-8 encoding
    mock_file.assert_called_once_with('/path/to/encoding_test.json', 'r',
                                      encoding='utf-8')

    response_data = json.loads(response.data)
    assert response_data['text'] == "Special chars: àáâãäåæçèéêë"
