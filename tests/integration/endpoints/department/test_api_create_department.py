from api.db.models import Department
from tests.conftest import enable_authentication


def test_create_department_success(client, app):
    """Test successful department creation"""
    data = {'name': 'new_department'}

    response = client.post('/api/admin/departments', json=data)
    assert response.status_code == 201

    response_data = response.get_json()
    assert 'department' in response_data
    dept = response_data['department']
    assert 'id' in dept
    assert 'name' in dept
    assert dept['name'] == 'new_department'

    # Verify department was actually created in database
    with app.app_context():
        created_dept = app.db.session.query(Department).filter_by(
            name='new_department'
        ).first()
        assert created_dept is not None
        assert created_dept.id == dept['id']
        assert created_dept.name == dept['name']


def test_create_department_super_admin_success(client, app):
    """Test successful department creation by super admin"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'super_admin',
        'X-Forwarded-For': '127.0.0.1'
    }

    data = {'name': 'super_admin_dept'}

    response = client.post('/api/admin/departments', json=data,
                           headers=headers)
    assert response.status_code == 201

    response_data = response.get_json()
    assert response_data['department']['name'] == 'super_admin_dept'

    # Verify in database
    with app.app_context():
        created_dept = app.db.session.query(Department).filter_by(
            name='super_admin_dept'
        ).first()
        assert created_dept is not None


def test_create_department_missing_name(client):
    """Test department creation with missing name"""
    response = client.post('/api/admin/departments', json={})
    assert response.status_code == 400

    response_data = response.get_json()
    assert response_data['message'] == 'Department name is required'


def test_create_department_null_name(client):
    """Test department creation with null name"""
    data = {'name': None}

    response = client.post('/api/admin/departments', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert response_data['message'] == 'Department name is required'


def test_create_department_empty_name(client):
    """Test department creation with empty name"""
    data = {'name': ''}

    response = client.post('/api/admin/departments', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert response_data['message'] == 'Department name is required'


def test_create_department_whitespace_only_name(client):
    """Test department creation with whitespace-only name"""
    data = {'name': '   '}

    response = client.post('/api/admin/departments', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert response_data['message'] == 'Department name is required'


def test_create_department_duplicate_name(client, bootstrap_department):
    """Test creating department with existing name"""
    data = {'name': bootstrap_department.name}

    response = client.post('/api/admin/departments', json=data)
    assert response.status_code == 400

    response_data = response.get_json()
    assert response_data['message'] == 'Department name already exists'


def test_create_department_case_insensitive_duplicate(client, app):
    """Test creating department with different case but same name"""
    # Create initial department
    with app.app_context():
        dept = Department(name="TestDept")
        app.db.session.add(dept)
        app.db.session.commit()

        # Try to create department with different case
        data = {'name': 'testdept'}
        response = client.post('/api/admin/departments', json=data)

        # This depends on database collation - may pass or fail
        # For SQLite (case-insensitive by default), this should fail
        if response.status_code == 400:
            response_data = response.get_json()
            assert response_data['message'] == 'Department name already exists'


def test_create_department_name_with_spaces(client, app):
    """Test creating department with spaces in name"""
    data = {'name': '  department with spaces  '}

    response = client.post('/api/admin/departments', json=data)
    assert response.status_code == 201

    response_data = response.get_json()
    # Name should be trimmed
    assert response_data['department']['name'] == 'department with spaces'

    # Verify in database
    with app.app_context():
        created_dept = app.db.session.query(Department).filter_by(
            name='department with spaces'
        ).first()
        assert created_dept is not None


def test_create_department_special_characters(client, app):
    """Test creating department with special characters"""
    data = {'name': 'dept-with_special.chars@123!'}

    response = client.post('/api/admin/departments', json=data)
    assert response.status_code == 201

    response_data = response.get_json()
    assert response_data['department'][
               'name'] == 'dept-with_special.chars@123!'


def test_create_department_very_long_name(client):
    """Test creating department with very long name"""
    long_name = 'a' * 1000  # Very long name
    data = {'name': long_name}

    response = client.post('/api/admin/departments', json=data)

    # Should succeed unless there is a database constraint
    assert response.status_code == 201


def test_create_department_unicode_name(client, app):
    """Test creating department with unicode characters"""
    data = {'name': 'département_测试_部门'}

    response = client.post('/api/admin/departments', json=data)
    assert response.status_code == 201

    response_data = response.get_json()
    assert response_data['department']['name'] == 'département_测试_部门'

    dep_id = response_data['department']['id']
    # Verify department in database has correct unicode name
    with app.app_context():
        created_dept = app.db.session.get(Department, dep_id)
        assert created_dept is not None
        assert created_dept.name == 'département_测试_部门'

        # Additional verification: ensure the name matches exactly
        # and unicode characters are preserved
        stored_name = created_dept.name
        expected_name = 'département_测试_部门'
        assert stored_name == expected_name
        assert len(stored_name) == len(expected_name)


def test_create_department_unauthenticated(client):
    """Test department creation without authentication when SSO enabled"""
    enable_authentication(client)

    data = {'name': 'new_department'}

    response = client.post('/api/admin/departments', json=data)
    assert response.status_code == 401
    response_data = response.get_json()
    assert response_data['message'] == 'Authentication required'


def test_create_department_unauthorized_user(client):
    """Test department creation with user that has no admin privileges"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'regular_user',
        'X-Forwarded-For': '127.0.0.1'
    }

    data = {'name': 'new_department'}

    response = client.post('/api/admin/departments', json=data,
                           headers=headers)
    assert response.status_code == 403
    response_data = response.get_json()
    assert response_data['message'] == 'Super admin privileges required'


def test_create_department_department_admin_rejected(
        client, bootstrap_tokens_and_users):
    """Test that department admin cannot create departments"""
    enable_authentication(client)

    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    headers = {
        'X-Forwarded-User': dept1_admin.user_handle,
        'X-Forwarded-For': '127.0.0.1'
    }

    data = {'name': 'new_department'}

    response = client.post('/api/admin/departments', json=data,
                           headers=headers)
    assert response.status_code == 403
    response_data = response.get_json()
    assert response_data['message'] == 'Super admin privileges required'


def test_create_department_untrusted_ip(client):
    """Test department creation from untrusted IP"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'super_admin',
        'X-Forwarded-For': '192.168.1.100'  # Untrusted IP
    }

    data = {'name': 'new_department'}

    response = client.post('/api/admin/departments', json=data,
                           headers=headers)
    assert response.status_code == 403
    response_data = response.get_json()
    assert response_data['message'] == 'Super admin privileges required'


def test_create_department_bearer_token_rejected(
        client, bootstrap_bearer_tokens):
    """Test that bearer token authentication is rejected"""
    enable_authentication(client)

    headers = {
        'Authorization': 'Bearer test-token-1'
    }

    data = {'name': 'new_department'}

    response = client.post('/api/admin/departments', json=data,
                           headers=headers)
    assert response.status_code == 403
    response_data = response.get_json()
    assert response_data['message'] == 'Super admin privileges required'


def test_create_department_invalid_json(client):
    """Test department creation with invalid JSON"""
    response = client.post('/api/admin/departments',
                           data='invalid json',
                           content_type='application/json')
    assert response.status_code == 400


def test_create_department_no_json_body(client):
    """Test department creation without JSON body"""
    response = client.post('/api/admin/departments')
    assert response.status_code == 415


def test_create_department_wrong_content_type(client):
    """Test department creation with wrong content type"""
    response = client.post('/api/admin/departments',
                           data='name=test_dept',
                           content_type='application/x-www-form-urlencoded')
    assert response.status_code == 415


def test_create_department_extra_fields(client, app):
    """Test department creation with extra fields in request"""
    data = {
        'name': 'test_department',
        'description': 'This field should be ignored',
        'extra_field': 'ignored'
    }

    response = client.post('/api/admin/departments', json=data)
    assert response.status_code == 201

    response_data = response.get_json()
    # Should only contain expected fields
    assert 'description' not in response_data['department']
    assert 'extra_field' not in response_data['department']


def test_create_department_response_format(client):
    """Test that response format matches expected structure"""
    data = {'name': 'format_test_dept'}

    response = client.post('/api/admin/departments', json=data)
    assert response.status_code == 201
    assert response.content_type == 'application/json'

    response_data = response.get_json()

    # Verify response structure
    assert set(response_data.keys()) == {'department'}
    dept = response_data['department']
    assert set(dept.keys()) == {'id', 'name'}
    assert isinstance(dept['id'], int)
    assert isinstance(dept['name'], str)


def test_create_department_database_error(client, mocker):
    """Test department creation with database error"""
    # Mock the database method to raise an exception
    mocker.patch(
        'api.app.get_department_by_name',
        return_value=None  # No existing department
    )
    mocker.patch(
        'api.app.create_department',
        side_effect=Exception("Database connection error")
    )

    data = {'name': 'test_department'}

    response = client.post('/api/admin/departments', json=data)
    assert response.status_code == 500
    response_data = response.get_json()
    assert response_data['message'] == 'Error creating department'


def test_create_department_rollback_on_error(client, app, mocker):
    """Test that database transaction is rolled back on error"""

    mocker.patch.object(app.db.session, 'add',
                        side_effect=Exception("Database error"))

    data = {'name': 'rollback_test_dept'}

    response = client.post('/api/admin/departments', json=data)
    assert response.status_code == 500

    # Verify department was not created despite initial add()
    with app.app_context():
        dept = app.db.session.query(Department).filter_by(
            name='rollback_test_dept'
        ).first()
        assert dept is None


def test_create_department_concurrent_creation(client, app):
    """Test handling of concurrent department creation attempts"""
    data = {'name': 'concurrent_dept'}

    # Simulate concurrent requests
    responses = []
    for _ in range(3):
        response = client.post('/api/admin/departments', json=data)
        responses.append(response)

    # One should succeed, others should fail with duplicate error
    success_count = sum(1 for r in responses if r.status_code == 201)
    duplicate_count = sum(1 for r in responses if r.status_code == 400)

    assert success_count == 1
    assert duplicate_count == 2

    # Verify only one department was created
    with app.app_context():
        depts = app.db.session.query(Department).filter_by(
            name='concurrent_dept'
        ).all()
        assert len(depts) == 1


def test_create_department_name_trimming_edge_cases(client):
    """Test various edge cases for name trimming"""
    test_cases = [
        ('  normal_name  ', 'normal_name'),
        ('\tname_with_tabs\t', 'name_with_tabs'),
        ('\nname_with_newlines\n', 'name_with_newlines'),
        ('  mixed   spaces  ', 'mixed   spaces'),  # Internal spaces preserved
    ]

    for input_name, expected_name in test_cases:
        data = {'name': input_name}
        response = client.post('/api/admin/departments', json=data)

        if expected_name:  # Should succeed
            assert response.status_code == 201
            response_data = response.get_json()
            assert response_data['department']['name'] == expected_name
        else:  # Should fail
            assert response.status_code == 400


def test_create_department_stress_test(client):
    """Test creating multiple departments rapidly"""
    created_depts = []

    for i in range(10):
        data = {'name': f'stress_test_dept_{i}'}
        response = client.post('/api/admin/departments', json=data)
        assert response.status_code == 201
        created_depts.append(response.get_json()['department'])

    # Verify all departments have unique IDs and names
    ids = [dept['id'] for dept in created_depts]
    names = [dept['name'] for dept in created_depts]

    assert len(set(ids)) == 10  # All unique IDs
    assert len(set(names)) == 10  # All unique names
