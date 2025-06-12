import os
import shutil
import tempfile

import pytest
from api.app import create_app
from api.db.models import Metadata

UPLOAD_FOLDER = 'uploads'


@pytest.fixture(scope="session")
def app():
    """Create application for testing"""
    # Create a temporary directory for test uploads
    test_upload_dir = tempfile.mkdtemp(prefix='test_uploads_')

    # Test configuration
    config = {
        'TESTING': True,
        'UPLOAD_FOLDER': test_upload_dir,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # In-memory database
        'SQLALCHEMY_ECHO': False
    }

    app = create_app(config)

    # Create application context for the tests
    with app.app_context():
        yield app

    # Cleanup
    if os.path.exists(test_upload_dir):
        shutil.rmtree(test_upload_dir)


# scope="session" means it creates one instance for the entire test run
@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def uploads_folder(app):
    upload_folder = app.config['UPLOAD_FOLDER']

    # Clean up before test
    if os.path.exists(upload_folder):
        shutil.rmtree(upload_folder)
    os.makedirs(upload_folder, exist_ok=True)

    yield upload_folder

    # Clean up after test
    if os.path.exists(upload_folder):
        shutil.rmtree(upload_folder)


@pytest.fixture
def uploads_folder_with_files(app):
    # Clean up before the test just in case and create the uploads folder
    upload_folder = app.config['UPLOAD_FOLDER']

    if os.path.exists(upload_folder):
        shutil.rmtree(upload_folder)
    os.makedirs(upload_folder, exist_ok=True)

    # Test data files
    test_files = [
        ('tests/data/host-CIS_input-20250101T000000Z-NonPassing.json',
         'file_id1',
         'file1.json'),
        ('tests/data/cisinput-true.json', 'file_id2', 'file2.json'),
        ('tests/data/cisinput-false.json', 'file_id3', 'file3.json')
    ]

    with app.app_context():
        for src_file, file_id, dest_filename in test_files:
            # Verify source file exists
            assert os.path.exists(src_file), \
                   f"Test data file {src_file} not found"

            # Create destination directory
            dest_dir = os.path.join(upload_folder, file_id)
            os.makedirs(dest_dir, exist_ok=True)

            # Copy file
            dest_path = os.path.join(dest_dir, dest_filename)
            shutil.copyfile(src_file, dest_path)

            # Create database entry
            metadata = Metadata(
                id=file_id,
                filename=dest_filename,
                # Add other required fields as needed
            )

            app.db.session.add(metadata)

        app.db.session.commit()

    yield upload_folder

    # Cleanup
    with app.app_context():
        # Clear database
        app.db.session.query(Metadata).delete()
        app.db.session.commit()

    if os.path.exists(upload_folder):
        shutil.rmtree(upload_folder)


@pytest.fixture
def test_data(file_name: str):
    data_file = os.path.join('tests', 'data', file_name)
    assert os.path.exists(data_file)
    with open(data_file, 'r') as fs:
        yield fs.read()
