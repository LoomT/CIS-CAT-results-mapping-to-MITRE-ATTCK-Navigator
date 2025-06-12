import json


def test_get_files_metadata(client, uploads_folder_with_files):
    """Test retrieving files metadata without the aggregate parameter"""
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
        assert file_info['filename'] in ['file1.json', 'file2.json',
                                         'file3.json']


def test_get_files_with_verbose_false(client, uploads_folder_with_files):
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
