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
def uploads_folder_with_files():
    # Clean up before the test just in case and create the uploads folder
    shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    cis_data1 = os.path.join('tests', 'data', 'cisinput.json')
    cis_data2 = os.path.join('tests', 'data', 'cisinput-true.json')
    cis_data3 = os.path.join('tests', 'data', 'cisinput-false.json')

    # Assert that the data files exist
    assert os.path.exists(cis_data1)
    assert os.path.exists(cis_data2)
    assert os.path.exists(cis_data3)

    destination1 = os.path.join(UPLOAD_FOLDER, 'file_id1', 'file1.json')
    destination2 = os.path.join(UPLOAD_FOLDER, 'file_id2', 'file2.json')
    destination3 = os.path.join(UPLOAD_FOLDER, 'file_id3', 'file3.json')

    # Create id directories TODO with database, this should not be necessary
    os.makedirs(os.path.dirname(destination1), exist_ok=True)
    os.makedirs(os.path.dirname(destination2), exist_ok=True)
    os.makedirs(os.path.dirname(destination3), exist_ok=True)

    # Copy the data files to the uploads folder
    shutil.copyfile(cis_data1, destination1)
    shutil.copyfile(cis_data2, destination2)
    shutil.copyfile(cis_data3, destination3)

    yield UPLOAD_FOLDER

    # Clean up after the test
    shutil.rmtree(UPLOAD_FOLDER)


@pytest.fixture
def test_data(file_name: str):
    data_file = os.path.join('tests', 'data', file_name)
    assert os.path.exists(data_file)
    with open(data_file, 'r') as fs:
        yield fs.read()
