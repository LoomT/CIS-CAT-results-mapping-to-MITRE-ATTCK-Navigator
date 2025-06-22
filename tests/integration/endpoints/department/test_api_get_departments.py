import pytest

from api.db.models import DepartmentUser
from tests.conftest import enable_authentication


def test_get_departments_success_no_departments(client):
    """Test successful departments retrieval when no departments exist"""
    response = client.get('/api/admin/departments')

    assert response.status_code == 200
    data = response.get_json()

    assert 'departments' in data
    assert isinstance(data['departments'], list)
    assert len(data['departments']) == 0


def test_get_departments_success_with_departments(
        client, bootstrap_tokens_and_users):
    """Test successful departments retrieval when departments exist"""
    response = client.get('/api/admin/departments')

    assert response.status_code == 200
    data = response.get_json()

    assert 'departments' in data
    assert isinstance(data['departments'], list)
    assert len(
        data['departments']) == 2  # Two departments from bootstrap fixture

    # Verify department structure
    for dept in data['departments']:
        assert 'id' in dept
        assert 'name' in dept
        assert isinstance(dept['id'], int)
        assert isinstance(dept['name'], str)

    # Verify specific departments exist
    dept_names = [dept['name'] for dept in data['departments']]
    assert 'bearer_token_dept1' in dept_names
    assert 'bearer_token_dept2' in dept_names


def test_get_departments_super_admin_sees_all(
        client, bootstrap_tokens_and_users):
    """Test that super admin sees all departments"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'super_admin',
        'X-Forwarded-For': '127.0.0.1'
    }

    response = client.get('/api/admin/departments', headers=headers)
    assert response.status_code == 200

    data = response.get_json()
    assert len(data['departments']) == 2

    # Verify all departments present
    dept_names = [dept['name'] for dept in data['departments']]
    assert 'bearer_token_dept1' in dept_names
    assert 'bearer_token_dept2' in dept_names


def test_get_departments_department_admin_sees_own_only(
        client, bootstrap_tokens_and_users):
    """Test that department admin only sees their own department"""
    enable_authentication(client)

    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    headers = {
        'X-Forwarded-User': dept1_admin.user_handle,
        'X-Forwarded-For': '127.0.0.1'
    }

    response = client.get('/api/admin/departments', headers=headers)
    assert response.status_code == 200

    data = response.get_json()
    assert len(data['departments']) == 1

    dept = data['departments'][0]
    assert dept['name'] == 'bearer_token_dept1'
    assert dept['id'] == bootstrap_tokens_and_users['dept1'].id


def test_get_departments_different_department_admin(
        client, bootstrap_tokens_and_users):
    """Test that different department admin sees their own department"""
    enable_authentication(client)

    dept2_admin = bootstrap_tokens_and_users['dept2_admin']
    headers = {
        'X-Forwarded-User': dept2_admin.user_handle,
        'X-Forwarded-For': '127.0.0.1'
    }

    response = client.get('/api/admin/departments', headers=headers)
    assert response.status_code == 200

    data = response.get_json()
    assert len(data['departments']) == 1

    dept = data['departments'][0]
    assert dept['name'] == 'bearer_token_dept2'
    assert dept['id'] == bootstrap_tokens_and_users['dept2'].id


def test_get_departments_unauthenticated(client):
    """Test departments endpoint without authentication when SSO enabled"""
    enable_authentication(client)

    response = client.get('/api/admin/departments')
    assert response.status_code == 401

    data = response.get_json()
    assert data['message'] == 'Authentication required'


def test_get_departments_unauthorized_user(client, bootstrap_tokens_and_users):
    """Test departments endpoint with user that has no admin privileges"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'regular_user',
        'X-Forwarded-For': '127.0.0.1'
    }

    response = client.get('/api/admin/departments', headers=headers)
    assert response.status_code == 403

    data = response.get_json()
    assert data['message'] == 'Admin privileges required'


def test_get_departments_untrusted_ip(client):
    """Test departments endpoint from untrusted IP"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'super_admin',
        'X-Forwarded-For': '192.168.1.100'  # Untrusted IP
    }

    response = client.get('/api/admin/departments', headers=headers)
    assert response.status_code == 403

    data = response.get_json()
    assert data['message'] == 'Admin privileges required'


def test_get_departments_bearer_token_authentication_rejected(
        client, bootstrap_tokens_and_users):
    """
    Test that bearer token authentication is rejected for departments endpoint
    """
    enable_authentication(client)

    headers = {
        'Authorization': 'Bearer test-token-1'
    }

    response = client.get('/api/admin/departments', headers=headers)
    assert response.status_code == 403

    data = response.get_json()
    assert data['message'] == 'Admin privileges required'


def test_get_departments_response_format(client, bootstrap_department):
    """Test that response format matches expected structure"""
    response = client.get('/api/admin/departments')

    assert response.status_code == 200
    assert response.content_type == 'application/json'

    data = response.get_json()

    # Verify top-level structure
    assert set(data.keys()) == {'departments'}
    assert isinstance(data['departments'], list)

    # Verify department structure if departments exist
    if data['departments']:
        dept = data['departments'][0]
        expected_fields = {'id', 'name'}
        assert set(dept.keys()) == expected_fields
        assert isinstance(dept['id'], int)
        assert isinstance(dept['name'], str)


@pytest.mark.parametrize("name", [
    "a", "département_测试_部门", "with space"
])
def test_get_departments_valid_name_handling(client, app, name):
    """Test handling of departments with edge case names"""
    from api.db.models import Department

    with app.app_context():
        dept = Department(name=name)
        app.db.session.add(dept)
        app.db.session.commit()

        response = client.get('/api/admin/departments')
        assert response.status_code == 200

        data = response.get_json()
        assert len(data['departments']) == 1
        assert data['departments'][0]['name'] == name


def test_get_departments_database_error(client, mocker):
    """Test departments endpoint with database error"""
    # Mock the database method to raise an exception
    mocker.patch(
        'api.app.get_all_departments_with_access',
        side_effect=Exception("Database connection error")
    )

    response = client.get('/api/admin/departments')

    assert response.status_code == 500
    data = response.get_json()
    assert data['message'] == 'Error fetching departments'


def test_get_departments_special_characters_in_name(client, app):
    """Test departments with special characters in names"""
    from api.db.models import Department

    with app.app_context():
        # Create department with special characters
        dept = Department(name="dept-with_special.chars@123")
        app.db.session.add(dept)
        app.db.session.commit()

        response = client.get('/api/admin/departments')
        assert response.status_code == 200

        data = response.get_json()
        assert len(data['departments']) == 1
        assert data['departments'][0]['name'] == "dept-with_special.chars@123"


def test_get_departments_concurrent_access(client, bootstrap_tokens_and_users):
    """Test departments endpoint handles concurrent access properly"""
    # Simulate multiple concurrent requests
    responses = []

    for _ in range(5):
        response = client.get('/api/admin/departments')
        responses.append(response)

    # All requests should succeed
    for response in responses:
        assert response.status_code == 200
        data = response.get_json()
        assert 'departments' in data
        assert len(data['departments']) == 2


def test_get_departments_with_deleted_user_reference(
        client, app, bootstrap_tokens_and_users):
    """Test departments endpoint when user reference might be stale"""
    enable_authentication(client)

    dept1_admin = bootstrap_tokens_and_users['dept1_admin']

    # The first request should work
    headers = {
        'X-Forwarded-User': dept1_admin.user_handle,
        'X-Forwarded-For': '127.0.0.1'
    }

    response = client.get('/api/admin/departments', headers=headers)
    assert response.status_code == 200

    # Delete the user from the database
    with app.app_context():
        # Can't use dept1_admin since it's attached to another session
        user_to_delete = app.db.session.query(DepartmentUser).filter_by(
            user_handle=dept1_admin.user_handle,
            department_id=dept1_admin.department_id
        ).first()

        app.db.session.delete(user_to_delete)
        app.db.session.commit()

    # The second request should still work
    # (the user gets treated as a regular user)
    response = client.get('/api/admin/departments', headers=headers)
    assert response.status_code == 403  # No admin privileges now

    data = response.get_json()
    assert data['message'] == 'Admin privileges required'
