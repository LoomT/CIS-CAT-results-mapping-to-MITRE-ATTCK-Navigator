import json
from datetime import datetime

import pytest
from tests.conftest import enable_authentication


def test_get_files_metadata_verbose_true(client, bootstrap_full):
    """Test retrieving files metadata with verbose=true"""
    response = client.get('/api/files?verbose=true')

    assert response.status_code == 200
    data = response.get_json()

    # Should return the full metadata structure
    assert isinstance(data, dict)
    assert 'data' in data
    assert isinstance(data['data'], list)
    assert len(data['data']) == 3  # From bootstrap_full fixture

    # Verify each file has complete metadata
    for file_info in data['data']:
        assert 'id' in file_info
        assert 'filename' in file_info
        assert 'hostname' in file_info
        assert 'benchmark' in file_info
        assert 'result' in file_info
        assert 'time_created' in file_info
        assert file_info['id'] in ['file_id1', 'file_id2', 'file_id3']


def test_get_files_metadata_verbose_false(client, bootstrap_full):
    """Test retrieving files metadata with verbose=false"""
    response = client.get('/api/files?verbose=false')

    assert response.status_code == 200
    data = response.get_json()

    # Should return only IDs
    assert 'ids' in data
    assert isinstance(data['ids'], list)
    assert len(data['ids']) == 3
    assert set(data['ids']) == {'file_id1', 'file_id2', 'file_id3'}


def test_get_files_metadata_default_verbose(client, bootstrap_full):
    """
    Test retrieving files metadata without verbose parameter
    (should default to false)
    """
    response = client.get('/api/files')

    assert response.status_code == 200
    data = response.get_json()

    # Should default to verbose=false behavior
    assert 'ids' in data
    assert isinstance(data['ids'], list)
    assert len(data['ids']) == 3


def test_get_files_metadata_empty_database(client, uploads_folder):
    """Test retrieving files metadata when no files exist"""
    response = client.get('/api/files?verbose=true')

    assert response.status_code == 200
    data = response.get_json()

    assert 'data' in data
    assert isinstance(data['data'], list)
    assert len(data['data']) == 0


def test_get_files_metadata_empty_database_ids_only(client, uploads_folder):
    """Test retrieving file IDs when no files exist"""
    response = client.get('/api/files?verbose=false')

    assert response.status_code == 200
    data = response.get_json()

    assert 'ids' in data
    assert isinstance(data['ids'], list)
    assert len(data['ids']) == 0


def test_get_files_metadata_with_pagination(client, bootstrap_full):
    """Test pagination parameters"""
    # Test first page with page size 2
    response = client.get('/api/files?verbose=true&page=0&page_size=2')

    assert response.status_code == 200
    data = response.get_json()

    assert 'data' in data
    assert len(data['data']) <= 2  # Should return at most 2 items


def test_get_files_metadata_with_hostname_filtering(client, bootstrap_full):
    """Test filtering by various parameters"""
    response = client.get('/api/files?verbose=true&hostname=1')

    assert response.status_code == 200
    data = response.get_json()

    assert len(data['data']) == 1
    assert (data['data'][0]['filename'] ==
            'host-cis_input-20250101T000000Z-NonPassing.json')


def test_get_files_metadata_authentication_required(client, bootstrap_full):
    """Test that admin authentication is required"""
    enable_authentication(client)

    # Request without authentication should fail
    response = client.get('/api/files?verbose=true')

    assert response.status_code == 401
    data = response.get_json()
    assert data['message'] == 'Authentication required'


def test_get_files_metadata_super_admin_access(client, bootstrap_full):
    """Test that super admin can access all files"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'super_admin',
        'X-Forwarded-For': '127.0.0.1'
    }

    response = client.get('/api/files?verbose=true', headers=headers)

    assert response.status_code == 200
    data = response.get_json()

    assert 'data' in data
    assert len(data['data']) == 3  # Super admin sees all files


def test_get_files_metadata_department_admin_access(
        client, bootstrap_full
):
    """Test that department admin sees only their department's files"""
    enable_authentication(client)

    dept1_admin = bootstrap_full['dept1_admin']
    headers = {
        'X-Forwarded-User': dept1_admin.user_handle,
        'X-Forwarded-For': '127.0.0.1'
    }

    response = client.get('/api/files?verbose=true', headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    print(data)

    assert 'data' in data
    # Should only see files from dept1 (file_id1 and file_id2)
    file_ids = [item['id'] for item in data['data']]
    assert 'file_id1' in file_ids
    assert 'file_id2' in file_ids
    assert 'file_id3' not in file_ids  # This belongs to dept2


def test_get_files_metadata_unauthorized_user(client, bootstrap_full):
    """Test that non-admin users are rejected"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'regular_user',
        'X-Forwarded-For': '127.0.0.1'
    }

    response = client.get('/api/files?verbose=true', headers=headers)

    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == 'Admin privileges required'


def test_get_files_metadata_bearer_token_access(client, bootstrap_full):
    """Test that bearer token authentication is rejected"""
    enable_authentication(client)

    headers = {
        'Authorization': 'Bearer test-token-1'
    }

    response = client.get('/api/files?verbose=true', headers=headers)

    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == 'Admin privileges required'


def test_get_files_metadata_inactive_bearer_token(client, bootstrap_full):
    """Test that inactive bearer tokens are rejected"""
    enable_authentication(client)

    headers = {
        'Authorization': 'Bearer test-token-2'  # This token is inactive
    }

    response = client.get('/api/files?verbose=true', headers=headers)

    assert response.status_code == 401
    data = response.get_json()
    assert data['message'] == 'Authentication required'


def test_get_files_metadata_invalid_bearer_token(client, bootstrap_full):
    """Test that invalid bearer tokens are rejected"""
    enable_authentication(client)

    headers = {
        'Authorization': 'Bearer invalid-token'
    }

    response = client.get('/api/files?verbose=true', headers=headers)

    assert response.status_code == 401
    data = response.get_json()
    assert data['message'] == 'Authentication required'


def test_get_files_metadata_untrusted_ip(client, bootstrap_full):
    """Test that requests from untrusted IPs are rejected"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'super_admin',
        'X-Forwarded-For': '192.168.1.100'  # Untrusted IP
    }

    response = client.get('/api/files?verbose=true', headers=headers)

    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == 'Admin privileges required'


def test_get_files_metadata_strict_slashes_false(client, bootstrap_full):
    """
    Test that trailing slash is handled correctly
    due to strict_slashes=False
    """
    response1 = client.get('/api/files?verbose=true')
    response2 = client.get('/api/files/?verbose=true')

    assert response1.status_code == 200
    assert response2.status_code == 200

    data1 = response1.get_json()
    data2 = response2.get_json()

    # Both should return the same data
    assert data1 == data2


def test_get_files_metadata_database_error(client, bootstrap_full, mocker):
    """Test handling of database errors"""
    # Mock get_metadata to raise an exception
    mocker.patch(
        'api.app.get_metadata', side_effect=Exception("Database error")
    )

    response = client.get('/api/files?verbose=true')

    assert response.status_code == 500
    assert response.data == b"Internal server error"


@pytest.mark.parametrize("verbose,expected_key", [
    ('true', 'data'),
    ('True', 'data'),
    ('TRUE', 'data'),
    ('false', 'ids'),
    ('False', 'ids'),
    ('FALSE', 'ids'),
    ('invalid', 'ids'),  # Should default to false
    ('', 'ids'),  # Should default to false
])
def test_get_files_metadata_various_verbose_values(
        client, bootstrap_full, verbose, expected_key
):
    """Test various values for the verbose parameter"""
    response = client.get(f'/api/files?verbose={verbose}')
    assert response.status_code == 200

    data = response.get_json()
    if expected_key == 'data':
        assert 'data' in data
        assert 'ids' not in data
        assert isinstance(data["data"], list)
    else:
        assert 'ids' in data
        assert 'data' not in data
        assert isinstance(data["ids"], list)


def test_get_files_metadata_multiple_query_parameters(client, bootstrap_full):
    """Test with multiple query parameters"""
    response = client.get(
        '/api/files?verbose=true&page=0&page_size=10&hostname=host'
    )

    assert response.status_code == 200
    data = response.get_json()

    assert 'data' in data
    assert isinstance(data['data'], list)


def test_get_files_metadata_response_structure_verbose(client, bootstrap_full):
    """Test the detailed structure of verbose response"""
    response = client.get('/api/files?verbose=true')

    assert response.status_code == 200
    assert response.content_type == 'application/json'

    data = response.get_json()
    assert isinstance(data, dict)
    assert 'data' in data

    if len(data['data']) > 0:
        file_item = data['data'][0]
        # Verify expected fields are present
        expected_fields = ['id', 'filename', 'time_created']
        for field in expected_fields:
            assert field in file_item

        # Verify related objects are included
        if file_item.get('hostname'):
            assert isinstance(file_item['hostname'], dict)
            assert 'name' in file_item['hostname']

        if file_item.get('benchmark'):
            assert isinstance(file_item['benchmark'], dict)
            assert 'name' in file_item['benchmark']

        if file_item.get('result'):
            assert isinstance(file_item['result'], dict)
            assert 'name' in file_item['result']


def test_get_files_metadata_response_structure_ids_only(
        client, bootstrap_full
):
    """Test the structure of IDs-only response"""
    response = client.get('/api/files?verbose=false')

    assert response.status_code == 200
    assert response.content_type == 'application/json'

    data = response.get_json()
    assert isinstance(data, dict)
    assert 'ids' in data
    assert isinstance(data['ids'], list)

    for file_id in data['ids']:
        assert isinstance(file_id, str)
        assert len(file_id) > 0


def test_get_files_metadata_large_dataset_simulation(
        client, app, bootstrap_tokens_and_users
):
    """Test with a larger dataset"""
    with app.app_context():
        from api.db.models import Metadata, Hostname, Benchmark, Result

        # Create additional test data
        host = Hostname(name='test_host_large')
        bench = Benchmark(name='test_bench_large')
        result = Result(name='TestResult')
        app.db.session.add_all([host, bench, result])
        app.db.session.commit()

        # Create 50 metadata entries
        for i in range(50):
            metadata = Metadata(
                id=f'large_test_id_{i}',
                filename=f'large_test_file_{i}.json',
                department_id=bootstrap_tokens_and_users['dept1'].id,
                hostname=host,
                benchmark=bench,
                result=result
            )
            app.db.session.add(metadata)

        app.db.session.commit()

    response = client.get('/api/files?verbose=false')
    assert response.status_code == 200

    data = response.get_json()
    # Should include our test data plus bootstrap data
    assert len(data['ids']) >= 50


@pytest.mark.parametrize("start,end,expected", [
    ('20250101T000000Z', None, {'new', 'file_id1', 'file_id2', 'file_id3'}),
    ('20250102T000000Z', None, {'new'}),
    ('20230101T052502Z', None,
     {'less_old', 'new', 'file_id1', 'file_id2', 'file_id3'}),
    ('20221001T000000Z', '20251231T000000Z',
     {'old', 'less_old', 'new', 'file_id1', 'file_id2', 'file_id3'}),
    ('20250101T000000Z', '20250930T000000Z',
     {'file_id1', 'file_id2', 'file_id3'}),
    (None, '20250101T000000Z',
     {'old', 'less_old', 'file_id1', 'file_id2', 'file_id3'}),
    (None, '20240101T000000Z', {'old', 'less_old'}),
    (None, '20230101T000000Z', set()),
    (None, '20230101T060000Z', {'old', 'less_old'}),
    (None, '20230101T052501Z', {'old'}),
    ('20230101T052501Z', '20230101T052501Z', {'old'}),
    ('20230101T052502Z', '20230101T052503Z', {'less_old'}),
])
def test_get_files_metadata_time_filtering(
        client, app, bootstrap_full, start, end, expected
):
    """Test time-based filtering"""
    with app.app_context():
        from api.db.models import Metadata
        metadata1 = Metadata(
            id='old',
            filename='20230101T052501Z',
            time_created=datetime.fromisoformat('20230101T052501Z'),
        )
        metadata2 = Metadata(
            id='new',
            filename='20251001T020202Z',
            time_created=datetime.fromisoformat('20251001T020202Z'),
        )
        metadata3 = Metadata(
            id='less_old',
            filename='20230101T052502Z',
            time_created=datetime.fromisoformat('20230101T052502Z'),
        )
        app.db.session.add_all([metadata1, metadata2, metadata3])
        app.db.session.commit()

    url = '/api/files?verbose=true'
    start_param = f'&min_time={start}' if start else ''
    end_param = f'&max_time={end}' if end else ''
    response = client.get(
        url + start_param + end_param,
    )

    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data
    assert set(file['id'] for file in data['data']) == expected


def test_get_files_metadata_invalid_page_parameters(client, bootstrap_full):
    """Test handling of invalid pagination parameters"""
    test_cases = [
        '?page=-1',
        '?page=invalid',
        '?page_size=-1',
        '?page_size=invalid',
        '?page=0&page_size=0',
    ]

    for params in test_cases:
        response = client.get(f'/api/files{params}&verbose=true')
        # Should not crash, may return error or handle gracefully
        assert response.status_code in [200, 400]


def test_get_files_metadata_sql_injection_protection(client, bootstrap_full):
    """Test protection against SQL injection attempts"""
    malicious_params = [
        "?hostname='; DROP TABLE metadata; --",
        "?filename=test' OR '1'='1",
        "?benchmark=test'; SELECT * FROM metadata; --",
    ]

    for params in malicious_params:
        response = client.get(f'/api/files{params}&verbose=true')
        # Should not crash and should not return unexpected data
        assert response.status_code in [200, 400]

        if response.status_code == 200:
            data = response.get_json()
            assert 'data' in data
            # Should return normal data, not expose database structure
            assert isinstance(data['data'], list)


def test_get_files_metadata(client, bootstrap_full):
    """Test retrieving files metadata without the aggregate parameter"""
    file_names = [
        'host-cis_input-20250101T000000Z-NonPassing.json',
        'true-cis_input-20250101T000000Z.json',
        'false-cis_input2-20250101T000000Z-NonPassing.json'
    ]
    response = client.get('/api/files?verbose=true')

    assert response.status_code == 200
    data = json.loads(response.data)

    # Verify the structure of the response
    assert 'data' in data
    assert isinstance(data['data'], list)
    assert len(data['data']) == 3  # From the fixture we expect 3 files

    # Verify each file has the expected structure
    for file_info in data['data']:
        assert 'id' in file_info
        assert 'filename' in file_info
        assert file_info['id'] in ['file_id1', 'file_id2', 'file_id3']
        assert file_info['filename'] in file_names


def test_get_files_with_verbose_false(client, bootstrap_full):
    """Test retrieving files metadata with verbose=false"""
    response = client.get('/api/files?verbose=false')

    assert response.status_code == 200
    data = json.loads(response.data)

    # Verify the structure of the response
    assert 'ids' in data
    assert isinstance(data['ids'], list)
    assert len(data['ids']) == 3  # From the fixture we expect 3 files
    assert set(data['ids']) == {'file_id1', 'file_id2', 'file_id3'}


def test_get_files_empty_folder(client, uploads_folder):
    """Test retrieving files metadata from an empty folder"""
    response = client.get('/api/files?verbose=true')

    assert response.status_code == 200
    data = json.loads(response.data)

    # Verify the response structure
    assert 'data' in data
    assert isinstance(data['data'], list)
    assert len(data['data']) == 0  # Empty folder should return empty list
