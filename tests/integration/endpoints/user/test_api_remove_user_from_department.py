from api.db.models import Department, DepartmentUser
from tests.conftest import enable_authentication


def test_remove_user_from_department_success(client,
                                             bootstrap_tokens_and_users):
    """Test successfully removing an existing user from a department"""
    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    dept1 = bootstrap_tokens_and_users['dept1']

    data = {
        'department_id': dept1.id,
        'user_handle': dept1_admin.user_handle
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 200

    response_data = response.get_json()
    assert response_data[
               'message'] == 'User removed from department successfully'

    # Verify user was actually removed from database
    with client.application.app_context():
        dept_user = client.application.db.session.query(
            DepartmentUser).filter_by(
            department_id=dept1.id,
            user_handle=dept1_admin.user_handle
        ).first()
        assert dept_user is None


def test_remove_user_super_admin_success(client, bootstrap_tokens_and_users):
    """Test successfully removing user by super admin"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'super_admin',
        'X-Forwarded-For': '127.0.0.1'
    }

    dept2_admin = bootstrap_tokens_and_users['dept2_admin']
    dept2 = bootstrap_tokens_and_users['dept2']

    data = {
        'department_id': dept2.id,
        'user_handle': dept2_admin.user_handle
    }

    response = client.delete('/api/admin/department-users',
                             json=data, headers=headers)
    assert response.status_code == 200

    response_data = response.get_json()
    assert response_data[
               'message'] == 'User removed from department successfully'

    # Verify user was removed
    with client.application.app_context():
        dept_user = client.application.db.session.query(
            DepartmentUser).filter_by(
            department_id=dept2.id,
            user_handle=dept2_admin.user_handle
        ).first()
        assert dept_user is None


def test_remove_user_missing_department_id(client):
    """Test removing user with missing department_id"""
    data = {'user_handle': 'test_user'}

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert response_data[
               'message'] == 'Department ID and user handle are required'


def test_remove_user_missing_user_handle(client, bootstrap_department):
    """Test removing user with missing user_handle"""
    data = {'department_id': bootstrap_department.id}

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert response_data[
               'message'] == 'Department ID and user handle are required'


def test_remove_user_missing_both_fields(client):
    """Test removing user with both required fields missing"""
    data = {}

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert response_data[
               'message'] == 'Department ID and user handle are required'


def test_remove_user_null_department_id(client):
    """Test removing user with null department_id"""
    data = {
        'department_id': None,
        'user_handle': 'test_user'
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert response_data[
               'message'] == 'Department ID and user handle are required'


def test_remove_user_null_user_handle(client, bootstrap_department):
    """Test removing user with null user_handle"""
    data = {
        'department_id': bootstrap_department.id,
        'user_handle': None
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert response_data[
               'message'] == 'Department ID and user handle are required'


def test_remove_user_empty_user_handle(client, bootstrap_department):
    """Test removing user with empty user_handle"""
    data = {
        'department_id': bootstrap_department.id,
        'user_handle': ''
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert response_data[
               'message'] == 'Department ID and user handle are required'


def test_remove_user_whitespace_only_user_handle(client, bootstrap_department):
    """Test removing user with whitespace-only user_handle"""
    data = {
        'department_id': bootstrap_department.id,
        'user_handle': '   '
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert response_data[
               'message'] == 'Department ID and user handle are required'


def test_remove_user_user_handle_with_leading_trailing_spaces(client, app):
    """Test removing user with user_handle that has leading/trailing spaces"""
    with app.app_context():
        dept = Department(name="trim_test_dept")
        app.db.session.add(dept)
        app.db.session.commit()

        # Add user with trimmed handle
        user = DepartmentUser(
            department_id=dept.id,
            user_handle="trimmed_user"
        )
        app.db.session.add(user)
        app.db.session.commit()

        dept_id = dept.id

    data = {
        'department_id': dept_id,
        'user_handle': '  trimmed_user  '
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 200

    # Verify user was removed (handle should be trimmed in the API)
    with app.app_context():
        dept_user = app.db.session.query(DepartmentUser).filter_by(
            department_id=dept_id,
            user_handle='trimmed_user'
        ).first()
        assert dept_user is None


def test_remove_user_invalid_department_id_string(client):
    """Test removing user with invalid string department_id"""
    data = {
        'department_id': 'invalid_id',
        'user_handle': 'test_user'
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert response_data['message'] == 'Department ID must be an integer'


def test_remove_user_invalid_department_id_float(client):
    """Test removing user with float department_id"""
    data = {
        'department_id': 123.45,
        'user_handle': 'test_user'
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert response_data['message'] == 'Department ID must be an integer'


def test_remove_user_invalid_department_id_negative(client):
    """Test removing user with negative department_id"""
    data = {
        'department_id': -1,
        'user_handle': 'test_user'
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 404

    response_data = response.get_json()
    assert response_data['message'] == 'Department not found'


def test_remove_user_department_not_found(client):
    """Test removing user from non-existent department"""
    data = {
        'department_id': 99999,
        'user_handle': 'test_user'
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 404

    response_data = response.get_json()
    assert response_data['message'] == 'Department not found'


def test_remove_user_not_in_department(client, bootstrap_department):
    """Test removing user who is not in the department"""
    data = {
        'department_id': bootstrap_department.id,
        'user_handle': 'nonexistent_user'
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 404

    response_data = response.get_json()
    assert response_data['message'] == 'User not found in department'


def test_remove_user_from_wrong_department(client, bootstrap_tokens_and_users):
    """Test removing user from department they're not in"""
    # Try to remove dept1_admin from dept2
    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    dept2 = bootstrap_tokens_and_users['dept2']

    data = {
        'department_id': dept2.id,
        'user_handle': dept1_admin.user_handle
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 404

    response_data = response.get_json()
    assert response_data['message'] == 'User not found in department'

    # Verify user is still in their original department
    with client.application.app_context():
        dept1_user = client.application.db.session.query(
            DepartmentUser).filter_by(
            department_id=bootstrap_tokens_and_users['dept1'].id,
            user_handle=dept1_admin.user_handle
        ).first()
        assert dept1_user is not None


def test_remove_user_from_multiple_departments(client, app):
    """Test removing user from one department when they're in multiple"""
    with app.app_context():
        # Create departments
        dept1 = Department(name="multi_dept1")
        dept2 = Department(name="multi_dept2")
        app.db.session.add(dept1)
        app.db.session.add(dept2)
        app.db.session.commit()

        # Add user to both departments
        user1 = DepartmentUser(
            department_id=dept1.id,
            user_handle="multi_user"
        )
        user2 = DepartmentUser(
            department_id=dept2.id,
            user_handle="multi_user"
        )
        app.db.session.add(user1)
        app.db.session.add(user2)
        app.db.session.commit()

        dept1_id = dept1.id
        dept2_id = dept2.id

    # Remove user from first department
    data = {
        'department_id': dept1_id,
        'user_handle': 'multi_user'
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 200

    # Verify user is removed from dept1 but still in dept2
    with app.app_context():
        dept1_user = app.db.session.query(DepartmentUser).filter_by(
            department_id=dept1_id,
            user_handle='multi_user'
        ).first()
        assert dept1_user is None

        dept2_user = app.db.session.query(DepartmentUser).filter_by(
            department_id=dept2_id,
            user_handle='multi_user'
        ).first()
        assert dept2_user is not None


def test_remove_user_special_characters_in_handle(client, app):
    """Test removing user with special characters in handle"""
    with app.app_context():
        dept = Department(name="special_chars_dept")
        app.db.session.add(dept)
        app.db.session.commit()

        user = DepartmentUser(
            department_id=dept.id,
            user_handle="user.with-special_chars@domain.com"
        )
        app.db.session.add(user)
        app.db.session.commit()

        dept_id = dept.id

    data = {
        'department_id': dept_id,
        'user_handle': 'user.with-special_chars@domain.com'
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 200

    # Verify user was removed
    with app.app_context():
        dept_user = app.db.session.query(DepartmentUser).filter_by(
            department_id=dept_id,
            user_handle='user.with-special_chars@domain.com'
        ).first()
        assert dept_user is None


def test_remove_user_unicode_characters_in_handle(client, app):
    """Test removing user with unicode characters in handle"""
    with app.app_context():
        dept = Department(name="unicode_dept")
        app.db.session.add(dept)
        app.db.session.commit()

        user = DepartmentUser(
            department_id=dept.id,
            user_handle="ユーザー名"
        )
        app.db.session.add(user)
        app.db.session.commit()

        dept_id = dept.id

    data = {
        'department_id': dept_id,
        'user_handle': 'ユーザー名'
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 200

    # Verify user was removed
    with app.app_context():
        dept_user = app.db.session.query(DepartmentUser).filter_by(
            department_id=dept_id,
            user_handle='ユーザー名'
        ).first()
        assert dept_user is None


def test_remove_user_case_sensitivity(client, app):
    """Test case sensitivity in user handles"""
    with app.app_context():
        dept = Department(name="case_test_dept")
        app.db.session.add(dept)
        app.db.session.commit()

        # Add user with lowercase handle
        user = DepartmentUser(
            department_id=dept.id,
            user_handle="testuser"
        )
        app.db.session.add(user)
        app.db.session.commit()

        dept_id = dept.id

    # Try to remove with uppercase handle
    data = {
        'department_id': dept_id,
        'user_handle': 'TESTUSER'
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 404

    response_data = response.get_json()
    assert response_data['message'] == 'User not found in department'

    # Verify original user is still there
    with app.app_context():
        dept_user = app.db.session.query(DepartmentUser).filter_by(
            department_id=dept_id,
            user_handle='testuser'
        ).first()
        assert dept_user is not None


def test_remove_user_unauthenticated(client, bootstrap_tokens_and_users):
    """Test removing user without authentication when SSO enabled"""
    enable_authentication(client)

    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    dept1 = bootstrap_tokens_and_users['dept1']

    data = {
        'department_id': dept1.id,
        'user_handle': dept1_admin.user_handle
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 401

    response_data = response.get_json()
    assert response_data['message'] == 'Authentication required'


def test_remove_user_unauthorized_user(client, bootstrap_tokens_and_users):
    """Test removing user with user that has no admin privileges"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'regular_user',
        'X-Forwarded-For': '127.0.0.1'
    }

    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    dept1 = bootstrap_tokens_and_users['dept1']

    data = {
        'department_id': dept1.id,
        'user_handle': dept1_admin.user_handle
    }

    response = client.delete('/api/admin/department-users',
                             json=data, headers=headers)
    assert response.status_code == 403

    response_data = response.get_json()
    assert response_data['message'] == 'Super admin privileges required'


def test_remove_user_department_admin_rejected(client,
                                               bootstrap_tokens_and_users):
    """Test that department admin cannot remove users"""
    enable_authentication(client)

    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    dept1 = bootstrap_tokens_and_users['dept1']

    headers = {
        'X-Forwarded-User': dept1_admin.user_handle,
        'X-Forwarded-For': '127.0.0.1'
    }

    data = {
        'department_id': dept1.id,
        'user_handle': 'some_user'
    }

    response = client.delete('/api/admin/department-users',
                             json=data, headers=headers)
    assert response.status_code == 403

    response_data = response.get_json()
    assert response_data['message'] == 'Super admin privileges required'


def test_remove_user_untrusted_ip(client, bootstrap_tokens_and_users):
    """Test removing user from untrusted IP"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'super_admin',
        'X-Forwarded-For': '192.168.1.100'  # Untrusted IP
    }

    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    dept1 = bootstrap_tokens_and_users['dept1']

    data = {
        'department_id': dept1.id,
        'user_handle': dept1_admin.user_handle
    }

    response = client.delete('/api/admin/department-users',
                             json=data, headers=headers)
    assert response.status_code == 403

    response_data = response.get_json()
    assert response_data['message'] == 'Super admin privileges required'


def test_remove_user_bearer_token_rejected(client, bootstrap_tokens_and_users):
    """Test that bearer token authentication is rejected"""
    enable_authentication(client)

    headers = {
        'Authorization': 'Bearer test-token-1'
    }

    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    dept1 = bootstrap_tokens_and_users['dept1']

    data = {
        'department_id': dept1.id,
        'user_handle': dept1_admin.user_handle
    }

    response = client.delete('/api/admin/department-users',
                             json=data, headers=headers)
    assert response.status_code == 403

    response_data = response.get_json()
    assert response_data['message'] == 'Super admin privileges required'


def test_remove_user_invalid_json(client):
    """Test removing user with invalid JSON"""
    response = client.delete('/api/admin/department-users',
                             data='invalid json',
                             content_type='application/json')
    assert response.status_code == 400


def test_remove_user_no_json_body(client):
    """Test removing user with no JSON body"""
    response = client.delete('/api/admin/department-users')
    assert response.status_code == 415


def test_remove_user_wrong_content_type(client, bootstrap_tokens_and_users):
    """Test removing user with wrong content type"""
    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    dept1 = bootstrap_tokens_and_users['dept1']

    data = f'department_id={dept1.id}&user_handle={dept1_admin.user_handle}'
    response = client.delete('/api/admin/department-users',
                             data=data,
                             content_type='application/x-www-form-urlencoded')
    assert response.status_code == 415


def test_remove_user_extra_fields(client, bootstrap_tokens_and_users):
    """Test removing user with extra fields in JSON"""
    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    dept1 = bootstrap_tokens_and_users['dept1']

    data = {
        'department_id': dept1.id,
        'user_handle': dept1_admin.user_handle,
        'extra_field': 'extra_value',
        'another_field': 123
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 200

    # Should ignore extra fields and remove user successfully
    response_data = response.get_json()
    assert response_data[
               'message'] == 'User removed from department successfully'


def test_remove_user_response_format(client, bootstrap_tokens_and_users):
    """Test that response format matches expected structure"""
    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    dept1 = bootstrap_tokens_and_users['dept1']

    data = {
        'department_id': dept1.id,
        'user_handle': dept1_admin.user_handle
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 200
    assert response.content_type == 'application/json'

    response_data = response.get_json()

    # Verify response structure
    assert set(response_data.keys()) == {'message'}
    assert isinstance(response_data['message'], str)
    assert response_data[
               'message'] == 'User removed from department successfully'


def test_remove_user_database_error(client, bootstrap_tokens_and_users,
                                    mocker):
    """Test removing user with database error"""
    # Mock the database method to raise an exception
    mocker.patch(
        'api.app.remove_user_from_department',
        side_effect=Exception("Database connection error")
    )

    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    dept1 = bootstrap_tokens_and_users['dept1']

    data = {
        'department_id': dept1.id,
        'user_handle': dept1_admin.user_handle
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 500

    response_data = response.get_json()
    assert response_data['message'] == 'Error removing user from department'


def test_remove_user_rollback_on_error(client, app, mocker):
    """Test that database transaction is rolled back on error"""
    with app.app_context():
        # Create department and user
        dept = Department(name="rollback_test_dept")
        app.db.session.add(dept)
        app.db.session.commit()

        user = DepartmentUser(
            department_id=dept.id,
            user_handle="rollback_user"
        )
        app.db.session.add(user)
        app.db.session.commit()

        dept_id = dept.id

    # Mock remove_user_from_department to raise an exception
    mocker.patch(
        'api.app.remove_user_from_department',
        side_effect=Exception("Database error")
    )

    data = {
        'department_id': dept_id,
        'user_handle': 'rollback_user'
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 500

    # Verify user is still in database after failed operation
    with app.app_context():
        dept_user = app.db.session.query(DepartmentUser).filter_by(
            department_id=dept_id,
            user_handle='rollback_user'
        ).first()
        assert dept_user is not None


def test_remove_user_twice(client, bootstrap_tokens_and_users):
    """Test removing the same user twice"""
    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    dept1 = bootstrap_tokens_and_users['dept1']

    data = {
        'department_id': dept1.id,
        'user_handle': dept1_admin.user_handle
    }

    # First removal should succeed
    response1 = client.delete('/api/admin/department-users', json=data)
    assert response1.status_code == 200

    # Second removal should fail
    response2 = client.delete('/api/admin/department-users', json=data)
    assert response2.status_code == 404

    response_data = response2.get_json()
    assert response_data['message'] == 'User not found in department'


def test_remove_user_concurrent_removal(client, app):
    """Test removing the same user concurrently"""
    with app.app_context():
        dept = Department(name="concurrent_test_dept")
        app.db.session.add(dept)
        app.db.session.commit()

        user = DepartmentUser(
            department_id=dept.id,
            user_handle="concurrent_user"
        )
        app.db.session.add(user)
        app.db.session.commit()

        dept_id = dept.id

    data = {
        'department_id': dept_id,
        'user_handle': 'concurrent_user'
    }

    # Simulate concurrent requests
    responses = []
    for _ in range(3):
        response = client.delete('/api/admin/department-users', json=data)
        responses.append(response)

    # One should succeed, others should fail with not found
    success_count = sum(1 for r in responses if r.status_code == 200)
    not_found_count = sum(1 for r in responses if r.status_code == 404)

    assert success_count == 1
    assert not_found_count == 2


def test_remove_user_method_not_allowed(client, bootstrap_tokens_and_users):
    """Test that other HTTP methods are not allowed"""
    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    dept1 = bootstrap_tokens_and_users['dept1']

    data = {
        'department_id': dept1.id,
        'user_handle': dept1_admin.user_handle
    }

    # GET should not be allowed
    response = client.get('/api/admin/department-users', json=data)
    assert response.status_code == 405

    # PUT should not be allowed
    response = client.put('/api/admin/department-users', json=data)
    assert response.status_code == 405

    # PATCH should not be allowed
    response = client.patch('/api/admin/department-users', json=data)
    assert response.status_code == 405


def test_remove_user_trailing_slash(client, bootstrap_tokens_and_users):
    """Test removing user with trailing slash in URL"""
    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    dept1 = bootstrap_tokens_and_users['dept1']

    data = {
        'department_id': dept1.id,
        'user_handle': dept1_admin.user_handle
    }

    # URL with trailing slash should work
    response = client.delete('/api/admin/department-users/', json=data)
    assert response.status_code == 200

    response_data = response.get_json()
    assert response_data[
               'message'] == 'User removed from department successfully'


def test_remove_user_zero_department_id(client):
    """Test removing user with zero department_id"""
    data = {
        'department_id': 0,
        'user_handle': 'test_user'
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 404

    response_data = response.get_json()
    assert response_data['message'] == 'Department not found'


def test_remove_user_large_department_id(client):
    """Test removing user with very large department_id"""
    large_id = 999999999999999
    data = {
        'department_id': large_id,
        'user_handle': 'test_user'
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 404

    response_data = response.get_json()
    assert response_data['message'] == 'Department not found'


def test_remove_user_very_long_handle(client, bootstrap_department):
    """Test removing user with very long handle"""
    long_handle = 'a' * 1000
    data = {
        'department_id': bootstrap_department.id,
        'user_handle': long_handle
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 404

    response_data = response.get_json()
    assert response_data['message'] == 'User not found in department'


def test_remove_user_performance_with_many_users(client, app):
    """Test removal performance when department has many users"""
    with app.app_context():
        dept = Department(name="performance_test_dept")
        app.db.session.add(dept)
        app.db.session.commit()

        # Create many users
        users = []
        for i in range(100):
            user = DepartmentUser(
                department_id=dept.id,
                user_handle=f'perf_user_{i:04d}'
            )
            users.append(user)

        app.db.session.add_all(users)
        app.db.session.commit()

        dept_id = dept.id

    # Remove a specific user from the middle
    data = {
        'department_id': dept_id,
        'user_handle': 'perf_user_0050'
    }

    response = client.delete('/api/admin/department-users', json=data)
    assert response.status_code == 200

    # Verify correct user was removed and others remain
    with app.app_context():
        removed_user = app.db.session.query(DepartmentUser).filter_by(
            department_id=dept_id,
            user_handle='perf_user_0050'
        ).first()
        assert removed_user is None

        remaining_count = app.db.session.query(DepartmentUser).filter_by(
            department_id=dept_id
        ).count()
        assert remaining_count == 99
