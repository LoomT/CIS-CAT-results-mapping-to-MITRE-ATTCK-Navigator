import os


def test_get_file_found(client, monkeypatch):
    test_file_id = "test_id"
    test_file_name = "example.txt"

    def mock_isdir(path):
        return True if test_file_id in path else False

    def mock_listdir(path):
        return [test_file_name] if test_file_id in path else []

    monkeypatch.setattr(os.path, "isdir", mock_isdir)
    monkeypatch.setattr(os, "listdir", mock_listdir)

    def mock_send_file(filepath, as_attachment, download_name):
        assert filepath.endswith(test_file_name)
        assert as_attachment is True
        assert download_name == test_file_name
        return "File sent"

    monkeypatch.setattr("api.app.send_file", mock_send_file)
    response = client.get(f"/api/files/{test_file_id}")
    assert response.status_code == 200
    assert response.data == b"File sent"


def test_get_file_not_found(client, monkeypatch):
    test_file_id = "nonexistent_id"

    def mock_isdir(path):
        return False

    monkeypatch.setattr(os.path, "isdir", mock_isdir)
    response = client.get(f"/api/files/{test_file_id}")
    assert response.status_code == 404
    assert response.data == b"No file by this id found"


def test_get_file_empty_id_folder(client, monkeypatch):
    test_file_id = "test_id"

    def mock_isdir(path):
        return True if test_file_id in path else False

    def mock_listdir(path):
        return []

    monkeypatch.setattr(os.path, "isdir", mock_isdir)
    monkeypatch.setattr(os, "listdir", mock_listdir)
    response = client.get(f"/api/files/{test_file_id}")
    assert response.status_code == 500
    assert response.data == b"No file found"


def test_get_file_multiple_files(client, monkeypatch):
    test_file_id = "test_id"

    def mock_isdir(path):
        return True if test_file_id in path else False

    def mock_listdir(path):
        return ["file1.txt", "file2.txt"] if test_file_id in path else []

    monkeypatch.setattr(os.path, "isdir", mock_isdir)
    monkeypatch.setattr(os, "listdir", mock_listdir)
    response = client.get(f"/api/files/{test_file_id}")
    assert response.status_code == 500
    assert response.data == b"Multiple files found"


def test_get_file_exception(client, monkeypatch):
    test_file_id = "test_id"

    def mock_isdir(path):
        raise Exception("Unexpected error")

    monkeypatch.setattr(os.path, "isdir", mock_isdir)
    response = client.get(f"/api/files/{test_file_id}")
    assert response.status_code == 500
    assert b"Unexpected error" in response.data


def test_get_file_malicious_id(client):
    test_file_id = "..%5c..%5csecret"

    response = client.get(f"/api/files/{test_file_id}")
    assert response.status_code == 400
    assert response.data == b"Invalid file id"
