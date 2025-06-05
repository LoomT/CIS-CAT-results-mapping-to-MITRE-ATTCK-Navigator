import json


def test_get_files_metadata(client, uploads_folder_with_files):
    """Test retrieving files metadata without the aggregate parameter"""
    response = client.get('/api/files')

    assert response.status_code == 200
    data = json.loads(response.data)

    # Verify the structure of the response
    assert 'files' in data
    assert isinstance(data['files'], list)
    assert len(data['files']) == 3  # From the fixture we expect 3 files

    # Verify each file has the expected structure
    for file_info in data['files']:
        assert 'id' in file_info
        assert 'filename' in file_info
        assert file_info['id'] in ['file_id1', 'file_id2', 'file_id3']
        assert file_info['filename'] in ['file1.json', 'file2.json',
                                         'file3.json']


def test_get_files_with_aggregate_false(client, uploads_folder_with_files):
    """Test retrieving files metadata with aggregate=false"""
    response = client.get('/api/files?aggregate=false')

    assert response.status_code == 200
    data = json.loads(response.data)

    # Verify the structure of the response
    assert 'files' in data
    assert isinstance(data['files'], list)
    assert len(data['files']) == 3  # From the fixture we expect 3 files


def test_get_files_empty_folder(client, uploads_folder):
    """Test retrieving files metadata from an empty folder"""
    response = client.get('/api/files')

    assert response.status_code == 200
    data = json.loads(response.data)

    # Verify the response structure
    assert 'files' in data
    assert isinstance(data['files'], list)
    assert len(data['files']) == 0  # Empty folder should return empty list
