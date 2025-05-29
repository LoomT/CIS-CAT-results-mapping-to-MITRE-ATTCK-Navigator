import io
import json
import os


def test_no_file_in_request(client):
    """Test if save_file returns
     the correct response when no file is provided."""
    response = client.post('/api/files/', data={})
    assert response.status_code == 400
    assert response.get_data(as_text=True) == "No file part"


def test_empty_file_field(client):
    """Test if save_file handles an empty file field."""
    response = client.post('/api/files/', data={'file': (io.BytesIO(), '')})
    assert response.status_code == 400
    assert response.get_data(as_text=True) == "No selected file"


def test_invalid_json_file(client):
    """Test if save_file handles an invalid JSON file format."""
    data = {'file': (io.BytesIO(b'Invalid JSON content'), 'test.json')}
    response = client.post('/api/files/', data=data,
                           content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.get_data(as_text=True) == "Invalid file format"


def test_valid_file_upload(client, uploads_folder):
    """Test if save_file successfully processes and stores a valid file."""
    valid_json_content = {'key': 'value'}
    data = {
        'file': (
            io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
            'test.json'
        ),
    }
    response = client.post('/api/files/', data=data,
                           content_type='multipart/form-data')
    assert response.status_code == 201
    response_data = json.loads(response.get_data(as_text=True))
    assert 'id' in response_data
    assert response_data['filename'] == 'test.json'
    unique_id = response_data['id']
    file_path = os.path.join(uploads_folder, unique_id, 'test.json')
    assert os.path.exists(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        stored_content = json.load(f)
    assert stored_content == valid_json_content


def test_unexpected_error_on_save(client, monkeypatch):
    """Test if save_file handles unexpected errors gracefully."""
    def mock_os_makedirs(*args, **kwargs):
        raise OSError("Mocked error")

    monkeypatch.setattr(os, 'makedirs', mock_os_makedirs)
    valid_json_content = {'key': 'value'}
    data = {
        'file': (
            io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
            'test.json'
        ),
    }
    response = client.post('/api/files/', data=data,
                           content_type='multipart/form-data')
    assert response.status_code == 500
    assert response.get_data(
        as_text=True) == "Unexpected error while processing file"
