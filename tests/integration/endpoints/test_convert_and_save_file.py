import io
import os

import pytest

# txt files should be removed and tests refactored
# when proper file validation is added


@pytest.mark.parametrize("file_name,file_content,expected_status", [
    ("testinputcis.json", open('tests/testinputcis.json', 'rb').read(),  201)
])
def test_convert_and_save_file_success(client, file_name, file_content,
                                       expected_status):

    response = client.post('/api/files',
                           data={
                               'file': (io.BytesIO(file_content), file_name)
                           })
    assert response.status_code == expected_status
    assert response.content_type == "application/json"

    data = response.get_json()
    assert isinstance(data, dict)
    assert 'id' in data
    assert 'filename' in data
    assert data['filename'] == 'converted_' + file_name


def test_convert_and_save_file_no_file(client):
    response = client.post('/api/files')
    assert response.status_code == 400
    assert response.data.decode() == 'No file part'


def test_convert_and_save_file_empty_filename(client):
    data = {'file': (io.BytesIO(b"Sample content"), '')}
    response = client.post('/api/files', data=data)
    assert response.status_code == 400
    assert response.data.decode() == 'No selected file'


def test_convert_and_save_file_invalid_filename(client):
    data = {'file': (io.BytesIO(b"Sample content"), '//')}
    response = client.post('/api/files', data=data)
    assert response.status_code == 400
    assert response.data.decode() == 'Invalid filename'


def test_convert_and_save_file_server_error(client, monkeypatch):
    def mock_os_makedirs(*args, **kwargs):
        raise OSError("Mocked error")

    monkeypatch.setattr(os, 'makedirs', mock_os_makedirs)
    response = client.post('/api/files',
                           data={
                               'file': (
                                   io.BytesIO(b"Sample content"),
                                   "testfile.txt"
                               )
                           })
    assert response.status_code == 500
    assert "Unexpected error while processing file" in response.data.decode()
