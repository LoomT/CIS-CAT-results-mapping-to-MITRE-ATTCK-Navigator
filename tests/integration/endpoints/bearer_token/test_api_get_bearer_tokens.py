from datetime import datetime, timezone

from tests.conftest import enable_authentication


def test_get_bearer_tokens_success_with_tokens(
        client,
        bootstrap_bearer_tokens
):
    """Test successful retrieval of bearer tokens when tokens exist"""
    response = client.get('/api/admin/bearer-tokens')

    assert response.status_code == 200
    data = response.get_json()

    # Should have 2 tokens for the accessible department
    assert len(data['tokens']) == 2
    assert len(data['departments']) == 2

    machine1 = bootstrap_bearer_tokens['token1'].machine_name
    machine3 = bootstrap_bearer_tokens['token3'].machine_name

    assert ({machine1, machine3} ==
            set(token['machine_name'] for token in data['tokens']))


def test_get_bearer_tokens_success_empty_result(client):
    """Test bearer tokens endpoint when no tokens exist"""
    response = client.get('/api/admin/bearer-tokens')

    assert response.status_code == 200
    data = response.get_json()

    assert 'tokens' in data
    assert 'departments' in data
    assert len(data['tokens']) == 0
    assert len(data['departments']) == 0


def test_get_bearer_tokens_token_formatting(
        client,
        app,
        bootstrap_bearer_tokens
):
    """Test that token data is properly formatted"""
    response = client.get('/api/admin/bearer-tokens')

    assert response.status_code == 200
    data = response.get_json()

    tokens = data['tokens']
    assert len(tokens) == 2

    for token_data in tokens:
        # Verify datetime formatting
        assert 'created_at' in token_data
        created_at = token_data['created_at']
        # Should be ISO format string
        datetime.fromisoformat(created_at.replace('Z', '+00:00'))

        # last_used can be null or ISO format
        if token_data['last_used'] is not None:
            last_used = token_data['last_used']
            datetime.fromisoformat(last_used.replace('Z', '+00:00'))


def test_get_bearer_tokens_unauthenticated(client):
    """Test bearer tokens endpoint without authentication"""

    enable_authentication(client)

    response = client.get('/api/admin/bearer-tokens')
    assert response.status_code == 401
    data = response.get_json()
    assert data['message'] == 'Authentication required'


def test_get_bearer_tokens_unauthorized_user(client):
    """Test bearer tokens endpoint with user that has no admin privileges"""

    enable_authentication(client)

    # Simulate non-admin user
    headers = {
        'X-Forwarded-User': 'regular_user',
        'X-Forwarded-For': '127.0.0.1'
    }

    response = client.get('/api/admin/bearer-tokens', headers=headers)
    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == 'Admin privileges required'


def test_get_bearer_tokens_department_admin_access(
        client,
        app,
        bootstrap_tokens_and_users
):
    """Test that department admin only sees tokens for their departments"""

    enable_authentication(client)
    dept1_id = bootstrap_tokens_and_users['dept1'].id

    # Set up department admin user
    dept_user = bootstrap_tokens_and_users['dept1_admin']

    headers = {
        'X-Forwarded-User': dept_user.user_handle,
        'X-Forwarded-For': '127.0.0.1'
    }

    response = client.get('/api/admin/bearer-tokens', headers=headers)
    assert response.status_code == 200

    data = response.get_json()
    # Should only see tokens for their department
    assert len(data['tokens']) == 1
    for token in data['tokens']:
        assert token['department']['id'] == dept1_id


def test_get_bearer_tokens_super_admin_access(
        client,
        bootstrap_bearer_tokens
):
    """Test that super admin sees all tokens"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'super_admin',
        'X-Forwarded-For': '127.0.0.1'
    }

    response = client.get('/api/admin/bearer-tokens', headers=headers)
    assert response.status_code == 200

    data = response.get_json()
    # Should see all tokens (2 total since 1 is inactive)
    assert len(data['tokens']) == 2
    assert len(data['departments']) == 2


def test_get_bearer_tokens_database_error(client, app, mocker):
    """Test bearer tokens endpoint with database error"""
    # Mock the database method to raise an exception
    mocker.patch(
        'api.app.get_bearer_tokens_for_departments',
        side_effect=Exception("Database connection error"),
    )

    response = client.get('/api/admin/bearer-tokens')

    assert response.status_code == 500
    data = response.get_json()
    assert data['message'] == 'Error fetching bearer tokens'


def test_get_bearer_tokens_with_bearer_token_auth(
        client,
        app,
        bootstrap_bearer_tokens
):
    """Test that bearer token authentication is rejected for this endpoint"""
    enable_authentication(client)

    # Bearer tokens should not be able to access admin endpoints
    headers = {
        'Authorization': 'Bearer test-token-1'
    }

    response = client.get('/api/admin/bearer-tokens', headers=headers)
    # Should be rejected because bearer tokens don't have admin privileges
    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == 'Admin privileges required'


def test_get_bearer_tokens_response_format(
        client,
        app,
        bootstrap_bearer_tokens
):
    """Test that response format matches expected structure"""
    response = client.get('/api/admin/bearer-tokens')

    assert response.status_code == 200
    assert response.content_type == 'application/json'

    data = response.get_json()

    # Verify top-level structure
    assert set(data.keys()) == {'tokens', 'departments'}

    # Verify token structure
    if data['tokens']:
        token = data['tokens'][0]
        expected_token_fields = {
            'id', 'machine_name', 'department',
            'created_at', 'last_used', 'created_by', 'is_active'
        }
        assert set(token.keys()) == expected_token_fields
        assert set(token['department'].keys()) == {'id', 'name'}

    # Verify department structure
    if data['departments']:
        dept = data['departments'][0]
        expected_dept_fields = {'id', 'name'}
        assert set(dept.keys()) == expected_dept_fields


def test_get_bearer_tokens_with_null_last_used(
        client,
        app,
        bootstrap_department
):
    """Test handling of tokens with null last_used timestamp"""
    from api.db.models import BearerToken

    with app.app_context():
        # Create token with null last_used
        token = BearerToken(
            token="test-token-null",
            machine_name="machine_null",
            department_id=bootstrap_department.id,
            created_by="admin",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            last_used=None
        )
        app.db.session.add(token)
        app.db.session.commit()

        response = client.get('/api/admin/bearer-tokens')
        assert response.status_code == 200

        data = response.get_json()

        assert len(data['tokens']) == 1
        null_token = data['tokens'][0]

        assert null_token is not None
        assert null_token['last_used'] is None

        # Cleanup
        # app.db.session.delete(token)
        # app.db.session.commit()
