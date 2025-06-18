import io
import json
import os
import uuid
import pytest


@pytest.fixture(scope='session', autouse=True)
def bootstrap_department(app):
    """
    Create a department once, before any test is executed, and
    make it available through both `app.config` *and* as a fixture
    value (should a test want to depend on it explicitly).
    """
    with app.test_client() as c:                     # session-scoped client
        resp = c.post("/api/admin/departments", json={"name": "test"})
        assert resp.status_code == 201
        department = resp.get_json()   # {'id': …, 'name': …}

    # store globally so every test can get it through the app
    app.config["TEST_DEPARTMENT"] = department
    return department


def test_no_file_in_request(client, app):
    """Test if save_file returns
     the correct response when no file is provided."""
    response = client.post('/api/files/?department_id=' +
                           str(app.config['TEST_DEPARTMENT']
                               ['department']['id']), data={})
    assert response.status_code == 400
    assert response.get_data(as_text=True) == "No file part"


def test_empty_file_field(client, app):
    """Test if save_file handles an empty file field."""

    response = client.post('/api/files/?department_id=' +
                           str(app.config['TEST_DEPARTMENT']
                               ['department']['id']),
                           data={'file': (io.BytesIO(), '')},
                           content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.get_data(as_text=True) == "No selected file"


def test_invalid_json_file(client, app):
    """Test if save_file handles an invalid JSON file format."""
    data = {'file': (io.BytesIO(b'Invalid JSON content'), 'test.json')}
    response = client.post('/api/files/?department_id=' +
                           str(app.config['TEST_DEPARTMENT']
                               ['department']['id']), data=data,
                           content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.get_data(as_text=True) == "Invalid file format"


def test_insecure_filename(client, app):
    """Test handling of invalid filenames caught by secure_filename."""
    # Create a file with a name that would be sanitized to empty string
    # For example, filenames with only special characters like "../../../"
    invalid_filename = "../../../"
    valid_json_content = {'key': 'value'}
    data = {
        'file': (
            io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
            invalid_filename
        ),
    }

    response = client.post('/api/files/?department_id=' +
                           str(app.config['TEST_DEPARTMENT']
                               ['department']['id']), data=data,
                           content_type='multipart/form-data')

    assert response.status_code == 400
    assert response.get_data(as_text=True) == "Invalid filename"


def test_valid_file_upload(client, app, uploads_folder):
    """Test if save_file successfully processes and stores a valid file."""
    # benchmark-title is required in the JSON body for parsing
    valid_json_content = {'key': 'value', 'benchmark-title': 'BENCHMARK-TYPE'}
    filename = 'HOST-NAME-BENCHMARK-TYPE-20250506T093226Z.json'
    data = {
        'file': (
            io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
            filename
        ),
    }
    response = client.post('/api/files/?department_id=' +
                           str(app.config['TEST_DEPARTMENT']
                               ['department']['id']), data=data,
                           content_type='multipart/form-data')
    assert response.status_code == 201
    response_data = json.loads(response.get_data(as_text=True))
    assert 'id' in response_data
    assert response_data['filename'] == filename
    unique_id = response_data['id']
    file_path = os.path.join(uploads_folder, unique_id, filename)
    assert os.path.exists(file_path)
    with open(file_path, 'r', encoding='utf-8') as f:
        stored_content = json.load(f)
    assert stored_content == valid_json_content


def test_unexpected_error_on_save(client, app, mocker):
    """Test if save_file handles unexpected errors gracefully."""
    mocker.patch('os.makedirs', side_effect=OSError("Mocked error"))
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
        as_text=True) == "Internal Server Error"


def test_unique_id_collision(client, app, uploads_folder, mocker):
    """Test that the endpoint generates
     a new UUID when a collision is detected."""
    # Mock uuid.uuid4 to return a predetermined sequence of values
    first_id = "first-uuid-value"
    second_id = "second-uuid-value"

    # Setup our mock to return first_id first, then second_id
    mock_uuid = mocker.patch('uuid.uuid4')
    mock_uuid.side_effect = [
        uuid.UUID(int=int(hash(first_id)) & 0xFFFFFFFFFFFFFFFF),
        # First call returns first_id
        uuid.UUID(int=int(hash(second_id)) & 0xFFFFFFFFFFFFFFFF)
        # Second call returns second_id
    ]

    # Create a directory with the same
    # name as our first mocked UUID to force a collision
    collision_dir = os.path.join(uploads_folder, str(uuid.UUID(
        int=int(hash(first_id)) & 0xFFFFFFFFFFFFFFFF)))
    os.makedirs(collision_dir, exist_ok=True)

    # Now make the request,
    # which should detect the collision and use the second UUID
    # benchmark-title is required in the JSON body for parsing
    valid_json_content = {'key': 'value', 'benchmark-title': 'BENCHMARK-TYPE'}
    filename = 'HOST-NAME-BENCHMARK-TYPE-20250506T093226Z.json'
    data = {
        'file': (
            io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
            filename
        ),
    }

    response = client.post('/api/files/?department_id=' +
                           str(app.config['TEST_DEPARTMENT']
                               ['department']['id']), data=data,
                           content_type='multipart/form-data')
    # Verify the response
    assert response.status_code == 201
    response_data = json.loads(response.get_data(as_text=True))

    # The response should contain the second UUID
    # since the first one had a collision
    expected_id = str(uuid.UUID(int=int(hash(second_id)) & 0xFFFFFFFFFFFFFFFF))
    assert response_data['id'] == expected_id

    # Verify the file was saved with the second UUID
    file_path = os.path.join(uploads_folder, expected_id, filename)
    assert os.path.exists(file_path)

    # Verify the UUID generation was called twice
    # (once initially, once after collision)
    assert mock_uuid.call_count == 2
