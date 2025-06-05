import json


def test_aggregate_true_no_ids(
        client,
        uploads_folder_with_files
):
    """Test aggregating files with no ids provided"""
    response = client.get('/api/files/aggregate')

    assert response.status_code == 400
    assert response.data == b"No file ids provided"


def test_aggregate_true_valid_ids(
        client,
        uploads_folder_with_files,
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
        uploads_folder_with_files
):
    """Test aggregating files with an invalid id"""
    response = client.get(
        '/api/files/aggregate?id=file_id1&id=nonexistent_id'
    )

    assert response.status_code == 404
    assert response.data == b"No file by this id found"


def test_aggregate_true_error_handling(
        client,
        uploads_folder_with_files,
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
