from api.db.models import BearerToken
from tests.conftest import enable_authentication


def test_revoke_bearer_token_success(client, app, bootstrap_tokens_and_users):
    """Test successful bearer token revocation"""
    token_id = bootstrap_tokens_and_users['token1'].id

    response = client.delete(f'/api/admin/bearer-tokens/{token_id}')
    assert response.status_code == 200

    response_data = response.get_json()
    assert response_data['message'] == 'Token revoked successfully'


def test_revoke_bearer_token_authorized_success(client, app,
                                                bootstrap_tokens_and_users):
    """Test successful bearer token revocation"""
    enable_authentication(client)
    token_id = bootstrap_tokens_and_users['token1'].id
    user = bootstrap_tokens_and_users['dept1_admin']
    headers = {
        'X-Forwarded-User': user.user_handle,
        'X-Forwarded-For': '127.0.0.1'
    }

    response = client.delete(f'/api/admin/bearer-tokens/{token_id}',
                             headers=headers,)
    assert response.status_code == 200

    response_data = response.get_json()
    assert response_data['message'] == 'Token revoked successfully'


def test_revoke_bearer_token_not_found(client):
    """Test revoking non-existent bearer token"""
    response = client.delete('/api/admin/bearer-tokens/99999')
    assert response.status_code == 403

    response_data = response.get_json()
    assert response_data['message'] == 'You do not have access to this token'


def test_revoke_bearer_token_unauthorized_access(client, app,
                                                 bootstrap_tokens_and_users):
    """Test revoking token user doesn't have access to"""
    enable_authentication(client)
    token_id = bootstrap_tokens_and_users['token3'].id
    user = bootstrap_tokens_and_users['dept1_admin']
    headers = {
        'X-Forwarded-User': user.user_handle,
        'X-Forwarded-For': '127.0.0.1'
    }
    response = client.delete(f'/api/admin/bearer-tokens/{token_id}',
                             headers=headers)
    assert response.status_code == 403
    response_data = response.get_json()
    assert response_data['message'] == 'You do not have access to this token'

    # check that the token still exists in the db and is active
    with app.app_context():
        token = app.db.session.get(BearerToken, token_id)
        assert token is not None
        assert token.is_active is True


def test_revoke_bearer_token_unauthenticated(client):
    """Test bearer token revocation without authentication"""
    enable_authentication(client)
    response = client.delete('/api/admin/bearer-tokens/1')
    assert response.status_code == 401
    response_data = response.get_json()
    assert response_data['message'] == 'Authentication required'
