import os
import shutil
import tempfile
from datetime import datetime, timezone

import pytest
from api.app import create_app
from api.db.models import Metadata, BearerToken, Department, DepartmentUser, \
    Benchmark, Hostname, Result

UPLOAD_FOLDER = 'uploads'


@pytest.fixture
def app():
    """Create application for testing"""
    # Create a temporary directory for test uploads
    test_upload_dir = tempfile.mkdtemp(prefix='test_uploads_')

    # Test configuration
    config = {
        'TESTING': True,
        'UPLOAD_FOLDER': test_upload_dir,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # In-memory database
        'SQLALCHEMY_ECHO': False,
        'ENABLE_SSO': False
    }

    app = create_app(config)

    # Create application context for the tests
    with app.app_context():
        yield app

    # Cleanup
    if os.path.exists(test_upload_dir):
        shutil.rmtree(test_upload_dir)


# scope="session" means it creates one instance for the entire test run
@pytest.fixture
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
def bootstrap_full(app, bootstrap_tokens_and_users):
    # Clean up before the test just in case and create the uploads folder
    upload_folder = app.config['UPLOAD_FOLDER']

    if os.path.exists(upload_folder):
        shutil.rmtree(upload_folder)
    os.makedirs(upload_folder, exist_ok=True)

    with app.app_context():
        passing = Result(name='Passing')
        non_passing = Result(name='NonPassing')
        host_host = Hostname(name='host')
        host_true = Hostname(name='true')
        host_false = Hostname(name='false')
        bench1 = Benchmark(name='cis_input')
        bench2 = Benchmark(name='cis_input2')
        app.db.session.add_all([passing, non_passing, host_host, host_true,
                                host_false, bench1, bench2])

        # Test data files
        test_files = [
            ('host-cis_input-20250101T000000Z-NonPassing.json',
             'file_id1', bootstrap_tokens_and_users['dept1'].id,
             host_host, bench1, '20250101T000000Z', non_passing),
            ('true-cis_input-20250101T000000Z.json',
             'file_id2', bootstrap_tokens_and_users['dept1'].id,
             host_true, bench1, '20250101T000000Z', passing),
            ('false-cis_input2-20250101T000000Z-NonPassing.json',
             'file_id3', bootstrap_tokens_and_users['dept2'].id,
             host_false, bench2, '20250101T000000Z', non_passing),
        ]

        for file_name, file_id, dept_id, \
                hostname, bench_type, time, result_type in test_files:

            file_path = os.path.join('tests', 'data', file_name)
            # Verify source file exists
            assert os.path.exists(file_path), \
                   f"Test data file {file_path} not found"

            # Create destination directory
            dest_dir = os.path.join(upload_folder, file_id)
            os.makedirs(dest_dir, exist_ok=True)

            # Copy file
            dest_path = os.path.join(dest_dir, file_name)
            shutil.copyfile(file_path, dest_path)

            # Create database entry
            metadata = Metadata(
                id=file_id,
                filename=file_name,
                department_id=dept_id,
                hostname=hostname,
                benchmark=bench_type,
                result=result_type,
                time_created=datetime.fromisoformat(time),
                # Add other required fields as needed
            )

            app.db.session.add(metadata)

        app.db.session.commit()

    yield bootstrap_tokens_and_users

    if os.path.exists(upload_folder):
        shutil.rmtree(upload_folder)


@pytest.fixture
def test_data(file_name: str):
    data_file = os.path.join('tests', 'data', file_name)
    assert os.path.exists(data_file)
    with open(data_file, 'r') as fs:
        yield fs.read()


@pytest.fixture
def bootstrap_department(app):
    """Set up a department"""
    with app.app_context():
        # Create additional department for access control tests
        dept = Department(name="dept")
        app.db.session.add(dept)
        app.db.session.commit()
        yield dept


@pytest.fixture
def bootstrap_bearer_tokens(app):
    """Set up bearer tokens for testing"""

    with app.app_context():
        # Create additional department for access control tests
        bearer_token_dept1 = Department(name="bearer_token_dept1")
        bearer_token_dept2 = Department(name="bearer_token_dept2")
        app.db.session.add(bearer_token_dept1)
        app.db.session.add(bearer_token_dept2)
        app.db.session.commit()

        # Create bearer tokens
        tokens = []

        # Token for the test department
        token1 = BearerToken(
            token="test-token-1",
            machine_name="machine1",
            department_id=bearer_token_dept1.id,
            created_by="admin",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            last_used=datetime.now(timezone.utc)
        )
        tokens.append(token1)

        # Another token for the test department
        token2 = BearerToken(
            token="test-token-2",
            machine_name="machine2",
            department_id=bearer_token_dept1.id,
            created_by="admin",
            is_active=False,
            created_at=datetime.now(timezone.utc),
            last_used=None
        )
        tokens.append(token2)

        # Token for second department
        token3 = BearerToken(
            token="test-token-3",
            machine_name="machine3",
            department_id=bearer_token_dept2.id,
            created_by="other_admin",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            last_used=None
        )
        tokens.append(token3)

        for token in tokens:
            app.db.session.add(token)

        app.db.session.commit()

        yield {
            'token1': token1,
            'token2': token2,
            'token3': token3,
            'dept1': bearer_token_dept1,
            'dept2': bearer_token_dept2
        }


@pytest.fixture
def bootstrap_tokens_and_users(app, bootstrap_bearer_tokens):
    """Set up bearer tokens and users for testing"""
    dept1_admin = DepartmentUser(
        department_id=bootstrap_bearer_tokens['dept1'].id,
        user_handle="dept1_admin"
    )
    dept2_admin = DepartmentUser(
        department_id=bootstrap_bearer_tokens['dept2'].id,
        user_handle="dept2_admin"
    )
    app.db.session.add(dept1_admin)
    app.db.session.add(dept2_admin)
    app.db.session.commit()

    yield {
        'dept1_admin': dept1_admin,
        'dept2_admin': dept2_admin
    } | bootstrap_bearer_tokens


def enable_authentication(
        client,
        super_admins=None,
        trusted_ips=None,
):
    """Enable authentication for the client"""

    if super_admins is None:
        super_admins = {'super_admin'}
    if trusted_ips is None:
        trusted_ips = {'127.0.0.1'}

    with client.application.app_context():
        client.application.config['ENABLE_SSO'] = True
        client.application.config['SUPER_ADMINS'] = super_admins
        client.application.config['TRUSTED_IPS'] = trusted_ips
