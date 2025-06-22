from api.db.models import Department, DepartmentUser
from tests.conftest import enable_authentication


def test_add_user_to_department_success(client, bootstrap_department):
    """Test successfully adding a new user to a department"""
    data = {
        'department_id': bootstrap_department.id,
        'user_handle': 'new_user'
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 201

    response_data = response.get_json()
    assert response_data['message'] == 'User added to department successfully'

    # Verify user was actually added to database
    with (client.application.app_context()):
        dept_user = \
            client.application.db.session.query(DepartmentUser).filter_by(
                department_id=bootstrap_department.id,
                user_handle='new_user'
            ).first()
        assert dept_user is not None
        assert dept_user.department_id == bootstrap_department.id
        assert dept_user.user_handle == 'new_user'


def test_add_user_to_department_super_admin_success(
        client, bootstrap_department
):
    """Test successfully adding user by super admin"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'super_admin',
        'X-Forwarded-For': '127.0.0.1'
    }

    data = {
        'department_id': bootstrap_department.id,
        'user_handle': 'super_admin_user'
    }

    response = client.post('/api/admin/department-users',
                           json=data, headers=headers)
    assert response.status_code == 201

    response_data = response.get_json()
    assert response_data['message'] == 'User added to department successfully'

    # Verify user was added
    with client.application.app_context():
        dept_user = \
            client.application.db.session.query(DepartmentUser).filter_by(
                department_id=bootstrap_department.id,
                user_handle='super_admin_user'
            ).first()
        assert dept_user is not None


def test_add_user_missing_department_id(client):
    """Test adding user with missing department_id"""
    data = {'user_handle': 'test_user'}

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert (response_data['message'] ==
            'Department ID and user handle are required')


def test_add_user_missing_user_handle(client, bootstrap_department):
    """Test adding user with missing user_handle"""
    data = {'department_id': bootstrap_department.id}

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert (response_data['message'] ==
            'Department ID and user handle are required')


def test_add_user_missing_both_fields(client):
    """Test adding user with both required fields missing"""
    data = {}

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert (response_data['message'] ==
            'Department ID and user handle are required')


def test_add_user_null_department_id(client):
    """Test adding user with null department_id"""
    data = {
        'department_id': None,
        'user_handle': 'test_user'
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert (response_data['message'] ==
            'Department ID and user handle are required')


def test_add_user_null_user_handle(client, bootstrap_department):
    """Test adding user with null user_handle"""
    data = {
        'department_id': bootstrap_department.id,
        'user_handle': None
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert (response_data['message'] ==
            'Department ID and user handle are required')


def test_add_user_empty_user_handle(client, bootstrap_department):
    """Test adding user with empty user_handle"""
    data = {
        'department_id': bootstrap_department.id,
        'user_handle': ''
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert (response_data['message'] ==
            'Department ID and user handle are required')


def test_add_user_whitespace_only_user_handle(client, bootstrap_department):
    """Test adding user with whitespace-only user_handle"""
    data = {
        'department_id': bootstrap_department.id,
        'user_handle': '   '
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert (response_data['message'] ==
            'Department ID and user handle are required')


def test_add_user_user_handle_with_leading_trailing_spaces(
        client, bootstrap_department
):
    """Test adding user with user_handle that has leading/trailing spaces"""
    data = {
        'department_id': bootstrap_department.id,
        'user_handle': '  trimmed_user  '
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 201

    # Verify user was added with trimmed handle
    with client.application.app_context():
        dept_user = \
            client.application.db.session.query(DepartmentUser).filter_by(
                department_id=bootstrap_department.id,
                user_handle='trimmed_user'
            ).first()
        assert dept_user is not None


def test_add_user_invalid_department_id_string(client):
    """Test adding user with invalid string department_id"""
    data = {
        'department_id': 'invalid_id',
        'user_handle': 'test_user'
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert response_data['message'] == 'Department ID must be an integer'


def test_add_user_invalid_department_id_float(client):
    """Test adding user with float department_id"""
    data = {
        'department_id': 123.45,
        'user_handle': 'test_user'
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert response_data['message'] == 'Department ID must be an integer'


def test_add_user_invalid_department_id_negative(client):
    """Test adding user with negative department_id"""
    data = {
        'department_id': -1,
        'user_handle': 'test_user'
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 404

    response_data = response.get_json()
    assert response_data['message'] == 'Department not found'


def test_add_user_department_not_found(client):
    """Test adding user to non-existent department"""
    data = {
        'department_id': 99999,
        'user_handle': 'test_user'
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 404

    response_data = response.get_json()
    assert response_data['message'] == 'Department not found'


def test_add_user_already_in_same_department(
        client, bootstrap_tokens_and_users
):
    """Test adding user who is already in the same department"""
    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    dept1 = bootstrap_tokens_and_users['dept1']

    data = {
        'department_id': dept1.id,
        'user_handle': dept1_admin.user_handle
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert (response_data['message'] ==
            'User is already assigned to this department')


def test_add_user_already_in_different_department(
        client, bootstrap_tokens_and_users
):
    """
    Test adding user to a different department when they're already in another
    """
    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    dept2 = bootstrap_tokens_and_users['dept2']

    data = {
        'department_id': dept2.id,
        'user_handle': dept1_admin.user_handle
    }

    # Should succeed - users can be in multiple departments
    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 201

    response_data = response.get_json()
    assert response_data['message'] == 'User added to department successfully'

    # Verify user is now in both departments
    with client.application.app_context():
        dept_users = \
            client.application.db.session.query(DepartmentUser).filter_by(
                user_handle=dept1_admin.user_handle
            ).all()
        assert len(dept_users) == 2


def test_add_user_special_characters_in_handle(client, bootstrap_department):
    """Test adding user with special characters in handle"""
    data = {
        'department_id': bootstrap_department.id,
        'user_handle': 'user.with-special_chars@domain.com'
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 201

    # Verify user was added
    with client.application.app_context():
        dept_user = \
            client.application.db.session.query(DepartmentUser).filter_by(
                department_id=bootstrap_department.id,
                user_handle='user.with-special_chars@domain.com'
            ).first()
        assert dept_user is not None


def test_add_user_unicode_characters_in_handle(client, bootstrap_department):
    """Test adding user with unicode characters in handle"""
    data = {
        'department_id': bootstrap_department.id,
        'user_handle': 'ユーザー名'
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 201

    # Verify user was added
    with client.application.app_context():
        dept_user = \
            client.application.db.session.query(DepartmentUser).filter_by(
                department_id=bootstrap_department.id,
                user_handle='ユーザー名'
            ).first()
        assert dept_user is not None


def test_add_user_very_long_handle(client, bootstrap_department):
    """Test adding user with very long handle"""
    long_handle = 'a' * 1000  # Very long handle
    data = {
        'department_id': bootstrap_department.id,
        'user_handle': long_handle
    }

    response = client.post('/api/admin/department-users', json=data)
    # Should succeed unless there's a database constraint
    assert response.status_code == 201


def test_add_user_case_sensitivity(client, bootstrap_department):
    """Test case sensitivity in user handles"""
    # Add user with lowercase handle
    data1 = {
        'department_id': bootstrap_department.id,
        'user_handle': 'testuser'
    }
    response1 = client.post('/api/admin/department-users', json=data1)
    assert response1.status_code == 201

    # Add user with uppercase handle - should be treated as different user
    data2 = {
        'department_id': bootstrap_department.id,
        'user_handle': 'TESTUSER'
    }
    response2 = client.post('/api/admin/department-users', json=data2)
    assert response2.status_code == 201

    # Verify both users exist
    with client.application.app_context():
        users = client.application.db.session.query(DepartmentUser).filter_by(
            department_id=bootstrap_department.id
        ).filter(DepartmentUser.user_handle.in_(
            ['testuser', 'TESTUSER']
        )).all()
        assert len(users) == 2


def test_add_user_unauthenticated(client, bootstrap_department):
    """Test adding user without authentication when SSO enabled"""
    enable_authentication(client)

    data = {
        'department_id': bootstrap_department.id,
        'user_handle': 'test_user'
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 401

    response_data = response.get_json()
    assert response_data['message'] == 'Authentication required'


def test_add_user_unauthorized_user(client, bootstrap_department):
    """Test adding user with user that has no admin privileges"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'regular_user',
        'X-Forwarded-For': '127.0.0.1'
    }

    data = {
        'department_id': bootstrap_department.id,
        'user_handle': 'test_user'
    }

    response = client.post('/api/admin/department-users',
                           json=data, headers=headers)
    assert response.status_code == 403

    response_data = response.get_json()
    assert response_data['message'] == 'Super admin privileges required'


def test_add_user_department_admin_rejected(
        client, bootstrap_tokens_and_users
):
    """Test that department admin cannot add users"""
    enable_authentication(client)

    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    dept1 = bootstrap_tokens_and_users['dept1']

    headers = {
        'X-Forwarded-User': dept1_admin.user_handle,
        'X-Forwarded-For': '127.0.0.1'
    }

    data = {
        'department_id': dept1.id,
        'user_handle': 'new_user'
    }

    response = client.post('/api/admin/department-users',
                           json=data, headers=headers)
    assert response.status_code == 403

    response_data = response.get_json()
    assert response_data['message'] == 'Super admin privileges required'


def test_add_user_untrusted_ip(client, bootstrap_department):
    """Test adding user from untrusted IP"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'super_admin',
        'X-Forwarded-For': '192.168.1.100'  # Untrusted IP
    }

    data = {
        'department_id': bootstrap_department.id,
        'user_handle': 'test_user'
    }

    response = client.post('/api/admin/department-users',
                           json=data, headers=headers)
    assert response.status_code == 403

    response_data = response.get_json()
    assert response_data['message'] == 'Super admin privileges required'


def test_add_user_bearer_token_rejected(
        client, bootstrap_department, bootstrap_bearer_tokens
):
    """Test that bearer token authentication is rejected"""
    enable_authentication(client)

    headers = {
        'Authorization': 'Bearer test-token-1'
    }

    data = {
        'department_id': bootstrap_department.id,
        'user_handle': 'test_user'
    }

    response = client.post('/api/admin/department-users',
                           json=data, headers=headers)
    assert response.status_code == 403

    response_data = response.get_json()
    assert response_data['message'] == 'Super admin privileges required'


def test_add_user_invalid_json(client):
    """Test adding user with invalid JSON"""
    response = client.post('/api/admin/department-users',
                           data='invalid json',
                           content_type='application/json')
    assert response.status_code == 400


def test_add_user_no_json_body(client):
    """Test adding user with no JSON body"""
    response = client.post('/api/admin/department-users')
    assert response.status_code == 415


def test_add_user_wrong_content_type(client, bootstrap_department):
    """Test adding user with wrong content type"""
    data = f'department_id={bootstrap_department.id}&user_handle=test_user'
    response = client.post('/api/admin/department-users',
                           data=data,
                           content_type='application/x-www-form-urlencoded')
    assert response.status_code == 415


def test_add_user_extra_fields(client, bootstrap_department):
    """Test adding user with extra fields in JSON"""
    data = {
        'department_id': bootstrap_department.id,
        'user_handle': 'test_user',
        'extra_field': 'extra_value',
        'another_field': 123
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 201

    # Should ignore extra fields and create user successfully
    response_data = response.get_json()
    assert response_data['message'] == 'User added to department successfully'


def test_add_user_response_format(client, bootstrap_department):
    """Test that response format matches expected structure"""
    data = {
        'department_id': bootstrap_department.id,
        'user_handle': 'format_test_user'
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 201
    assert response.content_type == 'application/json'

    response_data = response.get_json()

    # Verify response structure
    assert set(response_data.keys()) == {'message'}
    assert isinstance(response_data['message'], str)
    assert response_data['message'] == 'User added to department successfully'


def test_add_user_database_error(client, bootstrap_department, mocker):
    """Test adding user with database error"""
    # Mock the database method to raise an exception
    mocker.patch(
        'api.app.add_user_to_department',
        side_effect=Exception("Database connection error")
    )

    data = {
        'department_id': bootstrap_department.id,
        'user_handle': 'error_test_user'
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 500

    response_data = response.get_json()
    assert response_data['message'] == 'Error adding user to department'


def test_add_user_rollback_on_error(client, app, mocker):
    """Test that database transaction is rolled back on error"""
    with app.app_context():
        # Create a department
        dept = Department(name="rollback_test_dept")
        app.db.session.add(dept)
        app.db.session.commit()
        dept_id = dept.id

    # Mock add_user_to_department to raise an exception
    mocker.patch(
        'api.app.add_user_to_department',
        side_effect=Exception("Database error")
    )

    data = {
        'department_id': dept_id,
        'user_handle': 'rollback_user'
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 500

    # Verify user was not added after failed operation
    with app.app_context():
        dept_user = app.db.session.query(DepartmentUser).filter_by(
            department_id=dept_id,
            user_handle='rollback_user'
        ).first()
        assert dept_user is None


def test_add_user_concurrent_addition(client, app):
    """Test adding the same user to the same department concurrently"""
    with app.app_context():
        dept = Department(name="concurrent_test_dept")
        app.db.session.add(dept)
        app.db.session.commit()
        dept_id = dept.id

    data = {
        'department_id': dept_id,
        'user_handle': 'concurrent_user'
    }

    # Simulate concurrent requests
    responses = []
    for _ in range(3):
        response = client.post('/api/admin/department-users', json=data)
        responses.append(response)

    # One should succeed, others should fail with duplicate error
    success_count = sum(1 for r in responses if r.status_code == 201)
    duplicate_count = sum(1 for r in responses if r.status_code == 400)

    assert success_count == 1
    assert duplicate_count == 2


def test_add_user_method_not_allowed(client, bootstrap_department):
    """Test that other HTTP methods are not allowed"""
    data = {
        'department_id': bootstrap_department.id,
        'user_handle': 'test_user'
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


def test_add_user_trailing_slash(client, bootstrap_department):
    """Test adding user with trailing slash in URL"""
    data = {
        'department_id': bootstrap_department.id,
        'user_handle': 'trailing_slash_user'
    }

    # URL with trailing slash should work
    response = client.post('/api/admin/department-users/', json=data)
    assert response.status_code == 201

    response_data = response.get_json()
    assert response_data['message'] == 'User added to department successfully'


def test_add_user_zero_department_id(client):
    """Test adding user with zero department_id"""
    data = {
        'department_id': 0,
        'user_handle': 'test_user'
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 404

    response_data = response.get_json()
    assert response_data['message'] == 'Department not found'


def test_add_user_large_department_id(client):
    """Test adding user with very large department_id"""
    large_id = 999999999999999
    data = {
        'department_id': large_id,
        'user_handle': 'test_user'
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 404

    response_data = response.get_json()
    assert response_data['message'] == 'Department not found'


def test_add_user_database_constraint_violation(client, app):
    """Test handling of database constraint violations"""
    with app.app_context():
        dept = Department(name="constraint_test_dept")
        app.db.session.add(dept)
        app.db.session.commit()

        # Manually add user to bypass API validation
        user = DepartmentUser(
            department_id=dept.id,
            user_handle="constraint_user"
        )
        app.db.session.add(user)
        app.db.session.commit()
        dept_id = dept.id

    # Try to add the same user again through API
    data = {
        'department_id': dept_id,
        'user_handle': 'constraint_user'
    }

    response = client.post('/api/admin/department-users', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert (response_data['message'] ==
            'User is already assigned to this department')
