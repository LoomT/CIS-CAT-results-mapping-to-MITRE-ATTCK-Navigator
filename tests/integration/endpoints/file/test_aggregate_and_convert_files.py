import json
import os

import pytest
from tests.conftest import enable_authentication


def test_aggregate_with_explicit_ids(client, bootstrap_full, mocker):
    """Test aggregating files with explicitly provided IDs"""
    # Mock the combine_results function to return predictable data
    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.return_value = {'aggregated': 'test_data', 'file_count': 2}

    response = client.get('/api/files/aggregate?id=file_id1&id=file_id2')

    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    assert (response.headers['Content-Disposition'] ==
            'attachment; filename=converted_aggregated_results.json')

    # Verify the response contains the mocked data
    response_data = json.loads(response.data)
    assert response_data == {'aggregated': 'test_data', 'file_count': 2}

    # Verify combine_results was called with the correct number of files
    assert mock_combine.call_count == 1
    args, _ = mock_combine.call_args
    assert isinstance(args[0], list)
    assert len(args[0]) == 2


def test_aggregate_single_file(client, bootstrap_full, mocker):
    """Test aggregating a single file"""
    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.return_value = {'single_file': 'data'}

    response = client.get('/api/files/aggregate?id=file_id1')

    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response_data = json.loads(response.data)
    assert response_data == {'single_file': 'data'}

    # Verify combine_results was called with one file
    args, _ = mock_combine.call_args
    assert len(args[0]) == 1


def test_aggregate_all_files_no_ids_provided(client, bootstrap_full, mocker):
    """Test aggregating all files when no IDs are explicitly provided"""
    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.return_value = {'all_files': 'aggregated'}

    # Request without specific IDs should aggregate all available files
    response = client.get('/api/files/aggregate')

    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    response_data = json.loads(response.data)
    assert response_data == {'all_files': 'aggregated'}

    # Should aggregate all files from bootstrap_full (3 files)
    args, _ = mock_combine.call_args
    assert len(args[0]) == 3


def test_aggregate_with_query_filters(client, bootstrap_full, mocker):
    """Test aggregating files with query filters instead of explicit IDs"""
    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.return_value = {'filtered': 'data'}

    # Use filter parameters instead of explicit IDs
    response = client.get('/api/files/aggregate?hostname=1&benchmark=1')

    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data == {'filtered': 'data'}
    args, _ = mock_combine.call_args
    assert len(args) == 1


def test_aggregate_nonexistent_file_id(client, bootstrap_full):
    """Test aggregating with a nonexistent file ID"""
    response = client.get('/api/files/aggregate?id=nonexistent_id')

    assert response.status_code == 404
    assert response.get_json()['message'] == "No file by this id found"


def test_aggregate_mixed_valid_invalid_ids(client, bootstrap_full):
    """Test aggregating with a mix of valid and invalid file IDs"""
    response = client.get('/api/files/aggregate?id=file_id1&id=nonexistent_id')

    assert response.status_code == 404
    assert response.get_json()['message'] == "No file by this id found"


def test_aggregate_invalid_file_id_format(client, bootstrap_full):
    """Test aggregating with malformed file IDs"""
    # Test with file ID containing invalid characters
    response = client.get('/api/files/aggregate?id=../../../etc/passwd')

    assert response.status_code == 400
    assert response.get_json()['message'] == "Invalid file id"


def test_aggregate_empty_database(client, uploads_folder):
    """Test aggregating when no files exist"""
    response = client.get('/api/files/aggregate')

    assert response.status_code == 404
    assert (response.get_json()['message'] ==
            "No file ids were found matching the query")


def test_aggregate_empty_database_with_explicit_ids(client, uploads_folder):
    """Test aggregating with explicit IDs when no files exist"""
    response = client.get('/api/files/aggregate?id=file_id1')

    assert response.status_code == 404
    assert response.get_json()['message'] == "No file by this id found"


def test_aggregate_file_read_error(client, bootstrap_full, mocker):
    """Test handling of file read errors"""
    # Mock open to raise an exception
    mocker.patch('builtins.open', side_effect=IOError("File read error"))

    response = client.get('/api/files/aggregate?id=file_id1')

    assert response.status_code == 500
    assert response.get_json()['message'] == "Internal Server Error"


def test_aggregate_json_parse_error(client, bootstrap_full, mocker):
    """Test handling of JSON parsing errors"""
    # Mock json.load to raise an exception
    mocker.patch(
        'json.load',
        side_effect=json.JSONDecodeError("Invalid JSON", "", 0)
    )

    response = client.get('/api/files/aggregate?id=file_id1')

    assert response.status_code == 500
    assert response.get_json()['message'] == "Internal Server Error"


def test_aggregate_combine_results_error(client, bootstrap_full, mocker):
    """Test handling of combine_results function errors"""
    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.side_effect = Exception("Combine function failed")

    response = client.get('/api/files/aggregate?id=file_id1')

    assert response.status_code == 500
    assert response.get_json()['message'] == "Internal Server Error"


def test_aggregate_by_id_with_authentication_enabled(
        client, bootstrap_full, mocker
):
    """Test aggregation with authentication enabled"""
    enable_authentication(client)
    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.return_value = {'auth_test': 'data'}

    # Test without authentication
    response = client.get('/api/files/aggregate?id=file_id1')
    assert response.status_code == 200

    # Test with super admin authentication
    headers = {
        'X-Forwarded-User': 'super_admin',
        'X-Forwarded-For': '127.0.0.1'
    }

    response = client.get('/api/files/aggregate?id=file_id1', headers=headers)
    assert response.status_code == 200


def test_aggregate_department_access_control(
        client, bootstrap_full, mocker
):
    """Test that users can only aggregate files from their departments"""
    enable_authentication(client)
    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.return_value = {'dept_data': 'test'}

    dept1_admin = bootstrap_full['dept1_admin']
    headers = {
        'X-Forwarded-User': dept1_admin.user_handle,
        'X-Forwarded-For': '127.0.0.1'
    }

    # Should only aggregate files from dept1 (file_id1, file_id2)
    response = client.get('/api/files/aggregate', headers=headers)
    assert response.status_code == 200

    # Verify only dept1 files were aggregated
    args, _ = mock_combine.call_args
    assert len(args[0]) == 2  # Only dept1 files


def test_aggregate_bearer_token_authentication(client, bootstrap_full, mocker):
    """Test aggregation using bearer token authentication"""
    enable_authentication(client)
    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.return_value = {'bearer_test': 'data'}

    headers = {
        'Authorization': 'Bearer test-token-1'
    }

    response = client.get('/api/files/aggregate?id=file_id1', headers=headers)
    assert response.status_code == 200

    response_data = json.loads(response.data)
    assert response_data == {'bearer_test': 'data'}


def test_aggregate_strict_slashes_false(client, bootstrap_full, mocker):
    """
    Test that trailing slash is handled correctly due to strict_slashes=False
    """
    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.return_value = {'slash_test': 'data'}

    response1 = client.get('/api/files/aggregate?id=file_id1')
    response2 = client.get('/api/files/aggregate/?id=file_id1')

    assert response1.status_code == 200
    assert response2.status_code == 200

    data1 = json.loads(response1.data)
    data2 = json.loads(response2.data)
    assert data1 == data2


def test_aggregate_large_number_of_files(
        client, app, bootstrap_tokens_and_users, mocker
):
    """Test aggregating a large number of files"""
    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.return_value = {'large_aggregation': 'success'}

    upload_folder = app.config['UPLOAD_FOLDER']

    with app.app_context():
        from api.db.models import Metadata, Hostname, Benchmark, Result

        # Create additional test entities
        host = Hostname(name='large_test_host')
        bench = Benchmark(name='large_test_bench')
        result = Result(name='LargeTestResult')
        app.db.session.add_all([host, bench, result])
        app.db.session.commit()

        # Create 20 test files
        file_ids = []
        for i in range(20):
            file_id = f'large_test_id_{i}'
            file_ids.append(file_id)

            # Create file on disk
            dest_dir = os.path.join(upload_folder, file_id)
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, f'test_file_{i}.json')
            with open(dest_path, 'w') as f:
                json.dump({'test': f'data_{i}'}, f)

            # Create database entry
            metadata = Metadata(
                id=file_id,
                filename=f'test_file_{i}.json',
                department_id=bootstrap_tokens_and_users['dept1'].id,
                hostname=host,
                benchmark=bench,
                result=result
            )
            app.db.session.add(metadata)

        app.db.session.commit()

    # Create query string with all file IDs
    id_params = '&'.join([f'id={file_id}' for file_id in file_ids])
    response = client.get(f'/api/files/aggregate?{id_params}')

    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data == {'large_aggregation': 'success'}

    # Verify all files were processed
    args, _ = mock_combine.call_args
    assert len(args[0]) == 20


def test_aggregate_duplicate_file_ids(client, bootstrap_full, mocker):
    """Test aggregating with duplicate file IDs"""
    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.return_value = {'duplicate_test': 'data'}

    # Request same file ID multiple times
    response = client.get(
        '/api/files/aggregate?id=file_id1&id=file_id1&id=file_id2'
    )

    assert response.status_code == 200

    # Should process all IDs, including duplicates
    args, _ = mock_combine.call_args
    assert len(args[0]) == 3  # All three IDs should be processed


def test_aggregate_response_headers(client, bootstrap_full, mocker):
    """Test that response headers are set correctly"""
    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.return_value = {'header_test': 'data'}

    response = client.get('/api/files/aggregate?id=file_id1')

    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    assert 'Content-Disposition' in response.headers
    assert (response.headers['Content-Disposition'] ==
            'attachment; filename=converted_aggregated_results.json')


def test_aggregate_method_not_allowed(client, bootstrap_full):
    """Test that other HTTP methods are not allowed"""
    # POST should not be allowed
    response = client.post('/api/files/aggregate')
    assert response.status_code == 405

    # PUT should not be allowed
    response = client.put('/api/files/aggregate')
    assert response.status_code == 405

    # DELETE should not be allowed
    response = client.delete('/api/files/aggregate')
    assert response.status_code == 405


def test_aggregate_concurrent_requests(client, bootstrap_full, mocker):
    """Test handling of concurrent aggregation requests"""
    import threading

    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.return_value = {'concurrent_test': 'data'}

    results = []
    errors = []

    def make_request():
        try:
            response = client.get('/api/files/aggregate?id=file_id1')
            results.append(response.status_code)
        except Exception as e:
            errors.append(str(e))

    # Create multiple threads to make concurrent requests
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=make_request)
        threads.append(thread)

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # All requests should succeed
    assert len(errors) == 0
    assert all(status == 200 for status in results)
    assert len(results) == 5


@pytest.mark.parametrize("file_ids,expected_count", [
    (["file_id1"], 1),
    (["file_id1", "file_id2"], 2),
    (["file_id1", "file_id2", "file_id3"], 3),
])
def test_aggregate_parametrized_file_counts(
        client, bootstrap_full, mocker, file_ids, expected_count
):
    """Parametrized test for different numbers of files"""
    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.return_value = {'param_test': f'{expected_count}_files'}

    id_params = '&'.join([f'id={file_id}' for file_id in file_ids])
    response = client.get(f'/api/files/aggregate?{id_params}')

    assert response.status_code == 200
    args, _ = mock_combine.call_args
    assert len(args[0]) == expected_count


def test_aggregate_special_characters_in_query(client, bootstrap_full):
    """Test aggregation with special characters in query parameters"""
    # Test with URL-encoded characters
    response = client.get(
        '/api/files/aggregate?hostname=%20test%20&benchmark=test%26data'
    )

    # Should not crash, may return 404 if no matching files
    assert response.status_code in [200, 404]


def test_aggregate_very_large_response(client, bootstrap_full, mocker):
    """Test aggregation that produces a very large response"""
    # Create a large response to test memory handling
    large_data = {'large_data': 'x' * 10000, 'array': list(range(1000))}
    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.return_value = large_data

    response = client.get('/api/files/aggregate?id=file_id1')

    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data == large_data


def test_aggregate_file_encoding_issues(
        client, app, bootstrap_tokens_and_users, mocker
):
    """Test aggregation with files that have encoding issues"""
    upload_folder = app.config['UPLOAD_FOLDER']

    with app.app_context():
        from api.db.models import Metadata

        # Create file with non-UTF8 content (this might cause issues)
        file_id = 'encoding_test_id'
        dest_dir = os.path.join(upload_folder, file_id)
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, 'encoding_test.json')

        # Write valid JSON with UTF-8 encoding
        with open(dest_path, 'w', encoding='utf-8') as f:
            json.dump({'test': 'data with unicode: üñíçødé'}, f)

        # Create database entry
        metadata = Metadata(
            id=file_id,
            filename='encoding_test.json',
            department_id=bootstrap_tokens_and_users['dept1'].id,
        )
        app.db.session.add(metadata)
        app.db.session.commit()

    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.return_value = {'encoding_test': 'success'}

    response = client.get(f'/api/files/aggregate?id={file_id}')

    assert response.status_code == 200


def test_aggregate_with_pagination_parameters(client, bootstrap_full, mocker):
    """Test aggregation with pagination parameters in query"""
    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.return_value = {'pagination_test': 'data'}

    # Test with pagination parameters (they should be ignored for aggregation)
    response = client.get('/api/files/aggregate?page=0&page_size=10')

    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert response_data == {'pagination_test': 'data'}


def test_aggregate_query_parameter_injection(client, bootstrap_full):
    """Test protection against query parameter injection"""
    malicious_queries = [
        "?id=file_id1'; DROP TABLE metadata; --",
        "?hostname=test' OR '1'='1",
        "?benchmark=test'; SELECT * FROM files; --",
    ]

    for query in malicious_queries:
        response = client.get(f'/api/files/aggregate{query}')
        # Should not crash and should not expose database structure
        assert response.status_code in [200, 400, 404]


def test_aggregate_case_sensitivity(client, bootstrap_full, mocker):
    """Test case sensitivity of file IDs"""
    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.return_value = {'case_test': 'data'}

    # Test with different case variations
    response1 = client.get('/api/files/aggregate?id=file_id1')
    response2 = client.get('/api/files/aggregate?id=FILE_ID1')

    # file_id1 should work, FILE_ID1 might not (depending on implementation)
    assert response1.status_code == 200

    # The uppercase version might fail if IDs are case-sensitive
    assert response2.status_code in [200, 404]


def test_aggregate_no_combine_results_function(client, bootstrap_full, mocker):
    """Test behavior when combine_results function is not available"""
    # Mock combine_results to not exist
    mocker.patch(
        'api.app.combine_results',
        side_effect=AttributeError("combine_results not found")
    )

    response = client.get('/api/files/aggregate?id=file_id1')

    assert response.status_code == 500
    assert response.get_json()['message'] == "Internal Server Error"


def test_aggregate_true_no_ids(
        client,
        bootstrap_full
):
    """Test aggregating files with no ids provided"""
    response = client.get('/api/files/aggregate')

    assert response.status_code == 200
    # assert response.data == b"No file ids provided"


def test_aggregate_true_valid_ids(
        client,
        bootstrap_full,
        mocker
):
    """Test aggregating files with valid ids"""
    # Mock the combine_results function to return a predictable result
    mock_combine = mocker.patch('api.app.combine_results')
    mock_combine.return_value = {'aggregated': 'data'}

    response = client.get(
        '/api/files/aggregate?id=file_id1&id=file_id2'
    )

    assert response.status_code == 200
    assert response.mimetype == 'application/json'
    assert (response.headers['Content-Disposition']
            == 'attachment; filename=converted_aggregated_results.json'
            )

    # Check the response data matches our mock return value
    assert json.loads(response.data) == {'aggregated': 'data'}

    # Verify combine_results was called with the correct data
    # This checks that our function properly loaded the files
    # and passed them to combine_results
    assert mock_combine.call_count == 1
    # Extract the arguments passed to combine_results
    args, _ = mock_combine.call_args
    # Verify the first argument is a list of loaded JSON data
    assert isinstance(args[0], list)
    assert len(args[0]) == 2  # Should be 2 files


def test_aggregate_true_invalid_id(
        client,
        bootstrap_full
):
    """Test aggregating files with an invalid id"""
    response = client.get(
        '/api/files/aggregate?id=file_id1&id=nonexistent_id'
    )

    assert response.status_code == 404
    assert response.get_json() == {'message': 'No file by this id found'}


def test_aggregate_true_error_handling(
        client,
        bootstrap_full,
        mocker
):
    """Test error handling during aggregation"""
    # Mock combine_results to raise an exception
    mocker.patch(
        'api.app.combine_results',
        side_effect=Exception("Test error")
    )

    response = client.get(
        '/api/files/aggregate?id=file_id1&id=file_id2')

    assert response.status_code == 500
    assert "Internal Server Error" in response.data.decode('utf-8')
