import io
import json
import os
import uuid
from datetime import datetime, timezone

from api.db.models import Metadata, Department, BearerToken
from tests.conftest import enable_authentication


def test_no_file_in_request(client, app, bootstrap_department):
    """Test if save_file returns
     the correct response when no file is provided."""
    dep_id = bootstrap_department.id
    response = client.post(f'/api/files/?department_id={dep_id}', data={})
    assert response.status_code == 400
    assert response.get_json()['message'] == "No file part"

    # Verify no database entries were created
    with app.app_context():
        assert app.db.session.query(Metadata).count() == 0


def test_empty_file_field(client, app, bootstrap_department):
    """Test if save_file handles an empty file field."""
    dep_id = bootstrap_department.id
    response = client.post(f'/api/files/?department_id={dep_id}',
                           data={'file': (io.BytesIO(), '')},
                           content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.get_json()['message'] == "No selected file"

    # Verify no database entries were created
    with app.app_context():
        assert app.db.session.query(Metadata).count() == 0


def test_invalid_json_file(client, app, bootstrap_department):
    """Test if save_file handles an invalid JSON file format."""
    dep_id = bootstrap_department.id
    data = {'file': (io.BytesIO(b'Invalid JSON content'), 'test.json')}
    response = client.post(f'/api/files/?department_id={dep_id}', data=data,
                           content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.get_json()['message'] == "Invalid file format"

    # Verify no database entries were created
    with app.app_context():
        assert app.db.session.query(Metadata).count() == 0


def test_insecure_filename(client, app, bootstrap_department):
    """Test handling of invalid filenames caught by secure_filename."""
    dep_id = bootstrap_department.id
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

    response = client.post(f'/api/files/?department_id={dep_id}',
                           data=data, content_type='multipart/form-data')

    assert response.status_code == 400
    assert response.get_json()['message'] == "Invalid filename"

    # Verify no database entries were created
    with app.app_context():
        assert app.db.session.query(Metadata).count() == 0


def test_valid_file_upload(client, app, uploads_folder, bootstrap_department):
    """Test if save_file successfully processes and stores a valid file."""
    # benchmark-title is required in the JSON body for parsing
    dep_id = bootstrap_department.id
    valid_json_content = {'key': 'value', 'benchmark-title': 'BENCHMARK-TYPE'}
    filename = 'HOST-NAME-BENCHMARK-TYPE-20250506T093226Z.json'
    data = {
        'file': (
            io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
            filename
        ),
    }
    response = client.post(f'/api/files/?department_id={dep_id}',
                           data=data, content_type='multipart/form-data')
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

    # Verify database state
    with app.app_context():
        metadata = app.db.session.query(Metadata).filter_by(
            id=unique_id).first()
        assert metadata is not None
        assert metadata.filename == filename
        assert metadata.department_id == dep_id
        assert metadata.ip_address is not None
        assert metadata.time_created is not None

        # Verify related entities were created
        assert metadata.benchmark is not None
        assert metadata.benchmark.name == 'BENCHMARK-TYPE'
        assert metadata.hostname is not None
        assert metadata.hostname.name == 'HOST-NAME'


def test_unexpected_error_on_save(client, app, mocker, bootstrap_department):
    """Test if save_file handles unexpected errors gracefully."""
    dep_id = bootstrap_department.id
    mocker.patch('os.makedirs', side_effect=OSError("Mocked error"))
    valid_json_content = {'key': 'value'}
    data = {
        'file': (
            io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
            'test.json'
        ),
    }
    response = client.post(f'/api/files/?department_id={dep_id}',
                           data=data, content_type='multipart/form-data')
    assert response.status_code == 500
    assert response.get_json()['message'] == "Internal Server Error"

    # Verify database rollback occurred
    with app.app_context():
        assert app.db.session.query(Metadata).count() == 0


def test_unique_id_collision(
        client, app, uploads_folder, mocker, bootstrap_department):
    """Test that the endpoint generates
     a new UUID when a collision is detected."""
    dep_id = bootstrap_department.id
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

    response = client.post(f'/api/files/?department_id={dep_id}',
                           data=data, content_type='multipart/form-data')
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

    # Verify database state
    with app.app_context():
        metadata = app.db.session.query(Metadata).filter_by(
            id=expected_id).first()
        assert metadata is not None
        assert metadata.filename == filename
        assert metadata.department_id == dep_id


# NEW COMPREHENSIVE TESTS

def test_no_department_id_supplied(client, app, uploads_folder):
    """Test error when no department_id is provided."""
    valid_json_content = {'key': 'value', 'benchmark-title': 'BENCHMARK-TYPE'}
    filename = 'HOST-NAME-BENCHMARK-TYPE-20250506T093226Z.json'
    data = {
        'file': (
            io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
            filename
        ),
    }

    # No department_id parameter
    response = client.post('/api/files/', data=data,
                           content_type='multipart/form-data')
    assert response.status_code == 403
    response_data = json.loads(response.get_data(as_text=True))
    assert response_data['message'] == 'No department supplied'

    # Verify no database entries were created
    with app.app_context():
        assert app.db.session.query(Metadata).count() == 0


def test_invalid_department_id_type(client, app, uploads_folder):
    """Test error when department_id is not an integer."""
    valid_json_content = {'key': 'value', 'benchmark-title': 'BENCHMARK-TYPE'}
    filename = 'HOST-NAME-BENCHMARK-TYPE-20250506T093226Z.json'
    data = {
        'file': (
            io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
            filename
        ),
    }

    # Invalid department_id
    response = client.post('/api/files/?department_id=invalid',
                           data=data, content_type='multipart/form-data')
    assert response.status_code == 403
    response_data = json.loads(response.get_data(as_text=True))
    assert response_data['message'] == 'No department supplied'

    # Verify no database entries were created
    with app.app_context():
        assert app.db.session.query(Metadata).count() == 0


def test_unauthorized_department_access(client, app, uploads_folder):
    """Test error when user doesn't have access to the specified department."""
    # Create a department that the default admin user doesn't have access to
    with app.app_context():
        unauthorized_dept = Department(name="unauthorized_dept")
        app.db.session.add(unauthorized_dept)
        app.db.session.commit()
        unauthorized_dept_id = unauthorized_dept.id

    valid_json_content = {'key': 'value', 'benchmark-title': 'BENCHMARK-TYPE'}
    filename = 'HOST-NAME-BENCHMARK-TYPE-20250506T093226Z.json'
    data = {
        'file': (
            io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
            filename
        ),
    }

    # Enable authentication to test department access control
    enable_authentication(client)

    # Try to upload with unauthorized department
    headers = {
        'X-Forwarded-User': 'regular_user',
        'X-Forwarded-For': '127.0.0.1'
    }
    response = client.post(f'/api/files/?department_id={unauthorized_dept_id}',
                           data=data, content_type='multipart/form-data',
                           headers=headers)
    assert response.status_code == 403
    response_data = json.loads(response.get_data(as_text=True))
    assert response_data[
               'message'] == 'Admin privileges required'

    # Verify no database entries were created
    with app.app_context():
        assert app.db.session.query(Metadata).count() == 0


def test_bearer_token_upload(client, app, uploads_folder,
                             bootstrap_bearer_tokens):
    """Test file upload using bearer token authentication."""
    token = bootstrap_bearer_tokens['token1'].token

    valid_json_content = {'key': 'value', 'benchmark-title': 'BENCHMARK-TYPE'}
    filename = 'HOST-NAME-BENCHMARK-TYPE-20250506T093226Z.json'
    data = {
        'file': (
            io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
            filename
        ),
    }

    # Use bearer token for authentication
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/api/files/', data=data,
                           content_type='multipart/form-data', headers=headers)

    assert response.status_code == 201
    response_data = json.loads(response.get_data(as_text=True))
    assert 'id' in response_data
    assert response_data['filename'] == filename

    # Verify database state
    with app.app_context():
        metadata = app.db.session.query(Metadata).filter_by(
            id=response_data['id']).first()
        assert metadata is not None
        assert metadata.department_id == bootstrap_bearer_tokens['dept1'].id

        # Verify bearer token last_used was updated
        updated_token = app.db.session.query(BearerToken).filter_by(
            token=token).first()
        assert updated_token.last_used is not None


def test_bearer_token_inactive(client, app, uploads_folder,
                               bootstrap_bearer_tokens):
    """Test file upload fails with inactive bearer token."""
    token = bootstrap_bearer_tokens['token2'].token  # This token is inactive

    valid_json_content = {'key': 'value', 'benchmark-title': 'BENCHMARK-TYPE'}
    filename = 'HOST-NAME-BENCHMARK-TYPE-20250506T093226Z.json'
    data = {
        'file': (
            io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
            filename
        ),
    }

    # Use inactive bearer token
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/api/files/', data=data,
                           content_type='multipart/form-data', headers=headers)

    assert response.status_code == 403

    # Verify no database entries were created
    with app.app_context():
        assert app.db.session.query(Metadata).count() == 0


def test_bearer_token_invalid(client, app, uploads_folder):
    """Test file upload fails with invalid bearer token."""
    valid_json_content = {'key': 'value', 'benchmark-title': 'BENCHMARK-TYPE'}
    filename = 'HOST-NAME-BENCHMARK-TYPE-20250506T093226Z.json'
    data = {
        'file': (
            io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
            filename
        ),
    }

    # Use invalid bearer token
    headers = {'Authorization': 'Bearer invalid-token'}
    response = client.post('/api/files/', data=data,
                           content_type='multipart/form-data', headers=headers)

    assert response.status_code == 403

    # Verify no database entries were created
    with app.app_context():
        assert app.db.session.query(Metadata).count() == 0


def test_metadata_extraction_and_relationships(client, app, uploads_folder,
                                               bootstrap_department):
    """Test that metadata extraction creates proper database relationships."""
    dep_id = bootstrap_department.id

    # Create JSON with specific structure to test metadata extraction
    valid_json_content = {
        'benchmark-title': 'Custom Benchmark Test',
        'result': 'PASS',
        'other-data': 'test'
    }
    filename = 'test-host-Custom_Benchmark_Test-20250506T093226Z-PASS.json'
    data = {
        'file': (
            io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
            filename
        ),
    }

    response = client.post(f'/api/files/?department_id={dep_id}',
                           data=data, content_type='multipart/form-data')

    assert response.status_code == 201
    response_data = json.loads(response.get_data(as_text=True))
    unique_id = response_data['id']

    # Verify database relationships
    with app.app_context():
        metadata = app.db.session.query(Metadata).filter_by(
            id=unique_id).first()
        assert metadata is not None

        # Check benchmark relationship
        assert metadata.benchmark is not None
        assert metadata.benchmark.name == 'Custom_Benchmark_Test'

        # Check hostname relationship
        assert metadata.hostname is not None
        assert metadata.hostname.name == 'test-host'

        # Check result relationship
        assert metadata.result is not None
        assert metadata.result.name == 'PASS'

        # Check department relationship
        assert metadata.department is not None
        assert metadata.department.id == dep_id
        assert metadata.department.name == bootstrap_department.name


def test_file_cleanup_on_database_error(client, app, uploads_folder,
                                        bootstrap_department, mocker):
    """Test that files are cleaned up when database operations fail."""
    dep_id = bootstrap_department.id

    # Mock database commit to fail
    mocker.patch.object(app.db.session, 'commit',
                        side_effect=Exception("Database error"))

    valid_json_content = {'key': 'value', 'benchmark-title': 'BENCHMARK-TYPE'}
    filename = 'HOST-NAME-BENCHMARK-TYPE-20250506T093226Z.json'
    data = {
        'file': (
            io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
            filename
        ),
    }

    response = client.post(f'/api/files/?department_id={dep_id}',
                           data=data, content_type='multipart/form-data')

    assert response.status_code == 500

    # Verify no files remain in uploads folder
    upload_dirs = [d for d in os.listdir(uploads_folder)
                   if os.path.isdir(os.path.join(uploads_folder, d))]
    assert len(upload_dirs) == 0

    # Verify database rollback occurred
    with app.app_context():
        assert app.db.session.query(Metadata).count() == 0


def test_missing_benchmark_title(client, app, uploads_folder,
                                 bootstrap_department):
    """Test error handling when benchmark-title is missing from JSON."""
    dep_id = bootstrap_department.id

    # JSON without benchmark-title
    invalid_json_content = {'key': 'value'}
    filename = 'HOST-NAME-BENCHMARK-TYPE-20250506T093226Z.json'
    data = {
        'file': (
            io.BytesIO(json.dumps(invalid_json_content).encode('utf-8')),
            filename
        ),
    }

    response = client.post(f'/api/files/?department_id={dep_id}',
                           data=data, content_type='multipart/form-data')

    assert response.status_code == 500

    # Verify no database entries were created
    with app.app_context():
        assert app.db.session.query(Metadata).count() == 0


def test_concurrent_uploads_unique_ids(client, app, uploads_folder,
                                       bootstrap_department):
    """Test that concurrent uploads get unique IDs."""
    dep_id = bootstrap_department.id

    def make_upload_request():
        valid_json_content = {'key': 'value',
                              'benchmark-title': 'BENCHMARK-TYPE'}
        filename = 'HOST-NAME-BENCHMARK-TYPE-20250506T093226Z.json'
        data = {
            'file': (
                io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
                filename
            ),
        }
        return client.post(f'/api/files/?department_id={dep_id}',
                           data=data, content_type='multipart/form-data')

    # Make multiple upload requests
    responses = []
    for _ in range(3):
        response = make_upload_request()
        assert response.status_code == 201
        responses.append(json.loads(response.get_data(as_text=True)))

    # Verify all IDs are unique
    unique_ids = [resp['id'] for resp in responses]
    assert len(unique_ids) == len(set(unique_ids))

    # Verify all entries exist in database
    with app.app_context():
        assert app.db.session.query(Metadata).count() == 3
        for unique_id in unique_ids:
            metadata = app.db.session.query(Metadata).filter_by(
                id=unique_id).first()
            assert metadata is not None


def test_special_characters_in_filename(client, app, uploads_folder,
                                        bootstrap_department):
    """Test handling of filenames with special characters."""
    dep_id = bootstrap_department.id

    # Filename with special characters that should be sanitized
    special_filename = '@#with$special%-BENCHMARK-TYPE-20250506T093226Z.json'
    valid_json_content = {'key': 'value', 'benchmark-title': 'BENCHMARK-TYPE'}
    data = {
        'file': (
            io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
            special_filename
        ),
    }

    response = client.post(f'/api/files/?department_id={dep_id}',
                           data=data, content_type='multipart/form-data')

    assert response.status_code == 201
    response_data = json.loads(response.get_data(as_text=True))

    # Verify sanitized filename in response
    assert 'filename' in response_data
    sanitized_filename = response_data['filename']

    # Verify database state
    with app.app_context():
        metadata = app.db.session.query(Metadata).filter_by(
            id=response_data['id']).first()
        assert metadata is not None
        assert metadata.filename == sanitized_filename


def test_large_json_file_upload(client, app, uploads_folder,
                                bootstrap_department):
    """Test upload of a large JSON file."""
    dep_id = bootstrap_department.id

    # Create a large JSON structure
    large_json_content = {
        'benchmark-title': 'LARGE-BENCHMARK',
        'data': ['item' + str(i) for i in range(1000)],
        'nested': {
            'level1': {
                'level2': {
                    'level3': 'deep_value'
                }
            }
        }
    }
    filename = 'HOST-NAME-LARGE-BENCHMARK-20250506T093226Z.json'
    data = {
        'file': (
            io.BytesIO(json.dumps(large_json_content).encode('utf-8')),
            filename
        ),
    }

    response = client.post(f'/api/files/?department_id={dep_id}',
                           data=data, content_type='multipart/form-data')

    assert response.status_code == 201
    response_data = json.loads(response.get_data(as_text=True))
    unique_id = response_data['id']

    # Verify file was stored correctly
    file_path = os.path.join(uploads_folder, unique_id, filename)
    assert os.path.exists(file_path)

    with open(file_path, 'r', encoding='utf-8') as f:
        stored_content = json.load(f)
    assert stored_content == large_json_content

    # Verify database state
    with app.app_context():
        metadata = app.db.session.query(Metadata).filter_by(
            id=unique_id).first()
        assert metadata is not None
        assert metadata.filename == filename


def test_ip_address_recording(client, app, uploads_folder,
                              bootstrap_department):
    """Test that IP addresses are properly recorded in metadata."""
    dep_id = bootstrap_department.id

    valid_json_content = {'key': 'value', 'benchmark-title': 'BENCHMARK-TYPE'}
    filename = 'HOST-NAME-BENCHMARK-TYPE-20250506T093226Z.json'
    data = {
        'file': (
            io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
            filename
        ),
    }

    # Make request with custom IP
    response = client.post(f'/api/files/?department_id={dep_id}',
                           data=data, content_type='multipart/form-data',
                           environ_base={'REMOTE_ADDR': '192.168.1.100'})

    assert response.status_code == 201
    response_data = json.loads(response.get_data(as_text=True))

    # Verify IP address was recorded
    with app.app_context():
        metadata = app.db.session.query(Metadata).filter_by(
            id=response_data['id']).first()
        assert metadata is not None
        assert metadata.ip_address == '192.168.1.100'


def test_bearer_token_timestamp_recording(client, app, uploads_folder,
                                          bootstrap_bearer_tokens):
    """
    Test that timestamps are properly recorded in bearer tokens.
    Timestamps are stored in UTC and are rounded to the nearest second.
    """
    token = bootstrap_bearer_tokens['token3']  # unused token

    # db does not store microseconds so floor the before time
    before_upload = datetime.now(timezone.utc).replace(microsecond=0)

    valid_json_content = {'key': 'value', 'benchmark-title': 'BENCHMARK-TYPE'}
    filename = 'HOST-NAME-BENCHMARK-TYPE-20250506T093226Z.json'
    data = {
        'file': (
            io.BytesIO(json.dumps(valid_json_content).encode('utf-8')),
            filename
        ),
    }
    headers = {'Authorization': f'Bearer {token.token}'}

    assert token.last_used is None

    response = client.post('/api/files/', data=data, headers=headers,
                           content_type='multipart/form-data')

    after_upload = datetime.now(timezone.utc)

    assert response.status_code == 201
    json.loads(response.get_data(as_text=True))

    assert token.last_used is not None
    # last used is stored in UTC but fetched without TZ
    last_used = token.last_used.replace(tzinfo=timezone.utc)
    assert before_upload <= last_used <= after_upload
