import os
import tempfile

import pytest


# txt files should be removed and tests refactored
# when proper file validation is added
@pytest.mark.parametrize("file_name,file_content,expected_status", [
    ("testfile.txt", b"Sample content", 201),
    ("testfile.txt", b"", 201),
    ("testfile.json", b"", 201),
    ("testfile.json", b"{ \"id\": 2}", 201),
])
def test_convert_and_save_file_success(client, file_name, file_content,
                                       expected_status):
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(file_content)
        temp.seek(0)
        temp_path = temp.name
    with open(temp_path, 'rb') as f:
        response = client.post('/api/files',
                               data={'file': (f, file_name)})
    assert response.status_code == expected_status
    assert response.content_type == "application/json"

    data = response.get_json()
    assert isinstance(data, dict)
    assert 'id' in data
    assert 'filename' in data
    assert data['filename'] == 'converted_' + file_name

    os.unlink(temp_path)


def test_convert_and_save_file_no_file(client):
    response = client.post('/api/files')
    assert response.status_code == 400
    assert response.data.decode() == 'No file part'


def test_convert_and_save_file_empty_filename(client):
    data = {'file': (tempfile.TemporaryFile(), '')}
    response = client.post('/api/files', data=data)
    assert response.status_code == 400
    assert response.data.decode() == 'No selected file'


def test_convert_and_save_file_invalid_filename(client):
    data = {'file': (tempfile.TemporaryFile(), '//')}
    response = client.post('/api/files', data=data)
    assert response.status_code == 400
    assert response.data.decode() == 'Invalid filename'


def test_convert_and_save_file_server_error(client, monkeypatch):
    def mock_os_makedirs(*args, **kwargs):
        raise OSError("Mocked error")

    monkeypatch.setattr(os, 'makedirs', mock_os_makedirs)
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(b"Sample content")
        temp.seek(0)
        temp_path = temp.name
    with open(temp_path, 'rb') as f:
        response = client.post('/api/files',
                               data={'file': (f, "testfile.txt")})
    assert response.status_code == 500
    assert "Mocked error" in response.data.decode()
    os.unlink(temp_path)
