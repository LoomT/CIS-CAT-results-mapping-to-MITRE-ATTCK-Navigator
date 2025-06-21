from api.db.models import BearerToken
from tests.conftest import enable_authentication


def test_create_bearer_token_success(client, app, bootstrap_department):
    """Test successful bearer token creation"""
    data = {
        'department_id': bootstrap_department.id,
        'machine_name': 'test_machine'
    }

    response = client.post('/api/admin/bearer-tokens', json=data)
    assert response.status_code == 201

    response_data = response.get_json()
    assert 'token' in response_data
    token_data = response_data['token']

    # Verify token structure includes the actual token
    assert 'id' in token_data
    assert 'token' in token_data  # Should include actual token on creation
    assert 'machine_name' in token_data
    assert 'department' in token_data
    assert 'created_by' in token_data
    assert 'is_active' in token_data
    assert 'created_at' in token_data

    assert token_data['machine_name'] == 'test_machine'
    assert token_data['department']['id'] == bootstrap_department.id
    assert token_data['department']['name'] == bootstrap_department.name
    assert token_data['created_by'] == 'admin'
    assert token_data['is_active'] is True

    with app.app_context():
        token = app.db.session.get(BearerToken, token_data['id'])
        assert token is not None
        token_data.pop('token')
        assert token.to_dict() == token_data


def test_create_bearer_token_authorized_success(
        client, app,
        bootstrap_tokens_and_users
):
    """Test successful bearer token creation for the correct department"""
    enable_authentication(client)
    user = bootstrap_tokens_and_users['dept1_admin']

    headers = {
        'X-Forwarded-User': user.user_handle,
        'X-Forwarded-For': '127.0.0.1'
    }

    data = {
        'department_id': user.department_id,
        'machine_name': 'test_machine'
    }

    response = client.post('/api/admin/bearer-tokens', json=data,
                           headers=headers)
    assert response.status_code == 201

    response_data = response.get_json()
    assert 'token' in response_data
    token_data = response_data['token']

    with app.app_context():
        token = app.db.session.get(BearerToken, token_data['id'])
        assert token is not None
        token_data.pop('token')
        assert token.to_dict() == token_data


def test_create_bearer_token_missing_data(client):
    """Test bearer token creation with missing required data"""
    # Missing department_id
    response = client.post('/api/admin/bearer-tokens',
                           json={'machine_name': 'test'})
    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'Department ID and machine name are required'

    # Missing machine_name
    response = client.post('/api/admin/bearer-tokens',
                           json={'department_id': 1})
    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'Department ID and machine name are required'

    # Empty request body
    response = client.post('/api/admin/bearer-tokens', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'Department ID and machine name are required'


def test_create_bearer_token_invalid_department_id(client):
    """Test bearer token creation with invalid department ID"""
    data = {
        'department_id': 'invalid',
        'machine_name': 'test_machine'
    }

    response = client.post('/api/admin/bearer-tokens', json=data)
    assert response.status_code == 400
    response_data = response.get_json()
    assert response_data['message'] == 'Invalid department ID'


def test_create_bearer_token_unauthorized_department(
        client,
        app,
        bootstrap_department
):
    """Test creating token for department user doesn't have access to"""
    enable_authentication(client)

    dept_id = bootstrap_department.id
    data = {
        'department_id': dept_id,
        'machine_name': 'test_machine'
    }
    headers = {
        'X-Forwarded-User': 'regular_user',
        'X-Forwarded-For': '127.0.0.1'
    }
    response = client.post(
        '/api/admin/bearer-tokens',
        json=data,
        headers=headers
    )
    assert response.status_code == 403
    response_data = response.get_json()
    assert response_data['message'] == 'Admin privileges required'


def test_create_bearer_token_unauthenticated(
        client,
        bootstrap_department
):
    """Test bearer token creation without authentication"""
    enable_authentication(client)

    data = {
        'department_id': bootstrap_department.id,
        'machine_name': 'test_machine'
    }

    response = client.post('/api/admin/bearer-tokens', json=data)
    assert response.status_code == 401
    response_data = response.get_json()
    assert response_data['message'] == 'Authentication required'
