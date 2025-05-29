import os
import shutil

import pytest
from api.app import app as flask_app

UPLOAD_FOLDER = 'uploads'


# scope="session" means it creates one instance for the entire test run
@pytest.fixture(scope="session")
def client():
    flask_app.config.update({
        'TESTING': True,
        'UPLOAD_FOLDER': UPLOAD_FOLDER,
    })
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def runner():
    return flask_app.test_cli_runner()


@pytest.fixture
def uploads_folder():
    shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)  # just in case
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    yield UPLOAD_FOLDER
    shutil.rmtree(UPLOAD_FOLDER)


@pytest.fixture
def test_data(file_name: str):
    data_file = os.path.join('data', file_name)
    assert os.path.exists(data_file)
    with open(data_file, 'r') as fs:
        yield fs.read()
