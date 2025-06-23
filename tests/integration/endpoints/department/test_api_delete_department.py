from api.db.models import Department, DepartmentUser, BearerToken, Metadata
from tests.conftest import enable_authentication


def test_delete_department_success(client, app, bootstrap_department):
    """Test successful department deletion"""
    dept_id = bootstrap_department.id

    response = client.delete(f'/api/admin/departments/{dept_id}')
    assert response.status_code == 200

    response_data = response.get_json()
    assert response_data['message'] == 'Department deleted successfully'

    # Verify department was actually deleted from database
    with app.app_context():
        deleted_dept = app.db.session.get(Department, dept_id)
        assert deleted_dept is None


def test_delete_department_super_admin_success(client, app,
                                               bootstrap_department):
    """Test successful department deletion by super admin"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'super_admin',
        'X-Forwarded-For': '127.0.0.1'
    }

    dept_id = bootstrap_department.id

    response = client.delete(f'/api/admin/departments/{dept_id}',
                             headers=headers)
    assert response.status_code == 200

    response_data = response.get_json()
    assert response_data['message'] == 'Department deleted successfully'

    # Verify deletion in database
    with app.app_context():
        deleted_dept = app.db.session.get(Department, dept_id)
        assert deleted_dept is None


def test_delete_department_with_users_cascade(client, app):
    """Test department deletion cascades to delete associated users"""
    with app.app_context():
        # Create department with users
        dept = Department(name="dept_with_users")
        app.db.session.add(dept)
        app.db.session.commit()

        user1 = DepartmentUser(
            department_id=dept.id,
            user_handle="user1"
        )
        user2 = DepartmentUser(
            department_id=dept.id,
            user_handle="user2"
        )
        app.db.session.add(user1)
        app.db.session.add(user2)
        app.db.session.commit()

        dept_id = dept.id
        user1_id = user1.id
        user2_id = user2.id

    response = client.delete(f'/api/admin/departments/{dept_id}')
    assert response.status_code == 200

    # Verify department and users are deleted
    with app.app_context():
        deleted_dept = app.db.session.get(Department, dept_id)
        assert deleted_dept is None

        deleted_user1 = app.db.session.get(DepartmentUser, user1_id)
        deleted_user2 = app.db.session.get(DepartmentUser, user2_id)
        assert deleted_user1 is None
        assert deleted_user2 is None


def test_delete_department_with_bearer_tokens_cascade(client, app):
    """
    Test department deletion cascades to
    deactivate associated bearer tokens
    """
    with app.app_context():
        # Create department with bearer tokens
        dept = Department(name="dept_with_tokens")
        app.db.session.add(dept)
        app.db.session.commit()

        token1 = BearerToken(
            token="token1",
            machine_name="machine1",
            department_id=dept.id,
            created_by="admin",
            is_active=True
        )
        token2 = BearerToken(
            token="token2",
            machine_name="machine2",
            department_id=dept.id,
            created_by="admin",
            is_active=False
        )
        app.db.session.add(token1)
        app.db.session.add(token2)
        app.db.session.commit()

        dept_id = dept.id
        token1_id = token1.id
        token2_id = token2.id

    response = client.delete(f'/api/admin/departments/{dept_id}')
    assert response.status_code == 200

    # Verify department and tokens are deleted
    with app.app_context():
        deleted_dept = app.db.session.get(Department, dept_id)
        assert deleted_dept is None

        deleted_token1 = app.db.session.get(BearerToken, token1_id)
        deleted_token2 = app.db.session.get(BearerToken, token2_id)
        assert deleted_token1 is not None
        assert deleted_token1.is_active is False
        assert deleted_token1.department_id is None
        assert deleted_token2 is not None
        assert deleted_token2.is_active is False
        assert deleted_token2.department_id is None


def test_delete_department_with_metadata_references(client, app):
    """Test department deletion when metadata references it"""
    with app.app_context():
        # Create department with metadata references
        dept = Department(name="dept_with_metadata")
        app.db.session.add(dept)
        app.db.session.commit()

        metadata = Metadata(
            id="meta1",
            filename="test.json",
            department_id=dept.id
        )
        app.db.session.add(metadata)
        app.db.session.commit()

        dept_id = dept.id
        metadata_id = metadata.id

    response = client.delete(f'/api/admin/departments/{dept_id}')
    assert response.status_code == 200

    # Verify department is deleted but metadata remains with null department_id
    with app.app_context():
        deleted_dept = app.db.session.get(Department, dept_id)
        assert deleted_dept is None

        # metadata should remain but foreign key be nulled
        remaining_metadata = app.db.session.get(Metadata, metadata_id)
        assert remaining_metadata is not None
        assert remaining_metadata.department_id is None


def test_delete_department_not_found(client):
    """Test deleting non-existent department"""
    response = client.delete('/api/admin/departments/99999')
    assert response.status_code == 404

    response_data = response.get_json()
    assert response_data['message'] == 'Department not found'


def test_delete_department_invalid_id_string(client):
    """Test deleting department with invalid string ID"""
    response = client.delete('/api/admin/departments/invalid')
    assert response.status_code == 404


def test_delete_department_invalid_id_negative(client):
    """Test deleting department with negative ID"""
    response = client.delete('/api/admin/departments/-1')
    assert response.status_code == 404


def test_delete_department_zero_id(client):
    """Test deleting department with zero ID"""
    response = client.delete('/api/admin/departments/0')
    assert response.status_code == 404

    response_data = response.get_json()
    assert response_data['message'] == 'Department not found'


def test_delete_department_unauthenticated(client, bootstrap_department):
    """Test department deletion without authentication when SSO enabled"""
    enable_authentication(client)

    dept_id = bootstrap_department.id

    response = client.delete(f'/api/admin/departments/{dept_id}')
    assert response.status_code == 401
    response_data = response.get_json()
    assert response_data['message'] == 'Authentication required'

    # Verify department was not deleted
    with client.application.app_context():
        dept = client.application.db.session.get(Department, dept_id)
        assert dept is not None


def test_delete_department_unauthorized_user(client, bootstrap_department):
    """Test department deletion with user that has no admin privileges"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'regular_user',
        'X-Forwarded-For': '127.0.0.1'
    }

    dept_id = bootstrap_department.id

    response = client.delete(f'/api/admin/departments/{dept_id}',
                             headers=headers)
    assert response.status_code == 403
    response_data = response.get_json()
    assert response_data['message'] == 'Super admin privileges required'


def test_delete_department_department_admin_rejected(
        client, bootstrap_tokens_and_users):
    """Test that department admin cannot delete departments"""
    enable_authentication(client)

    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    dept_id = bootstrap_tokens_and_users['dept1'].id

    headers = {
        'X-Forwarded-User': dept1_admin.user_handle,
        'X-Forwarded-For': '127.0.0.1'
    }

    response = client.delete(f'/api/admin/departments/{dept_id}',
                             headers=headers)
    assert response.status_code == 403
    response_data = response.get_json()
    assert response_data['message'] == 'Super admin privileges required'


def test_delete_department_untrusted_ip(client, bootstrap_department):
    """Test department deletion from untrusted IP"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'super_admin',
        'X-Forwarded-For': '192.168.1.100'  # Untrusted IP
    }

    dept_id = bootstrap_department.id

    response = client.delete(f'/api/admin/departments/{dept_id}',
                             headers=headers)
    assert response.status_code == 403
    response_data = response.get_json()
    assert response_data['message'] == 'Super admin privileges required'


def test_delete_department_bearer_token_rejected(
        client, bootstrap_department, bootstrap_bearer_tokens):
    """Test that bearer token authentication is rejected"""
    enable_authentication(client)

    headers = {
        'Authorization': 'Bearer test-token-1'
    }

    dept_id = bootstrap_department.id

    response = client.delete(f'/api/admin/departments/{dept_id}',
                             headers=headers)
    assert response.status_code == 403
    response_data = response.get_json()
    assert response_data['message'] == 'Super admin privileges required'


def test_delete_department_response_format(client, bootstrap_department):
    """Test that response format matches expected structure"""
    dept_id = bootstrap_department.id

    response = client.delete(f'/api/admin/departments/{dept_id}')
    assert response.status_code == 200
    assert response.content_type == 'application/json'

    response_data = response.get_json()

    # Verify response structure
    assert set(response_data.keys()) == {'message'}
    assert isinstance(response_data['message'], str)
    assert response_data['message'] == 'Department deleted successfully'


def test_delete_department_database_error(client, bootstrap_department,
                                          mocker):
    """Test department deletion with database error"""
    # Mock the database method to raise an exception
    mocker.patch(
        'api.app.delete_department',
        side_effect=Exception("Database connection error")
    )

    dept_id = bootstrap_department.id

    response = client.delete(f'/api/admin/departments/{dept_id}')
    assert response.status_code == 500
    response_data = response.get_json()
    assert response_data['message'] == 'Error deleting department'


def test_delete_department_rollback_on_error(client, app, mocker):
    """Test that database transaction is rolled back on error"""
    with app.app_context():
        # Create a department
        dept = Department(name="rollback_test_dept")
        app.db.session.add(dept)
        app.db.session.commit()
        dept_id = dept.id

    # Mock delete_department to raise an exception
    mocker.patch(
        'api.app.delete_department',
        side_effect=Exception("Database error")
    )

    response = client.delete(f'/api/admin/departments/{dept_id}')
    assert response.status_code == 500

    # Verify department still exists after failed deletion
    with app.app_context():
        remaining_dept = app.db.session.get(Department, dept_id)
        assert remaining_dept is not None
        assert remaining_dept.name == "rollback_test_dept"


def test_delete_department_twice(client, app, bootstrap_department):
    """Test deleting the same department twice"""
    dept_id = bootstrap_department.id

    # First deletion should succeed
    response = client.delete(f'/api/admin/departments/{dept_id}')
    assert response.status_code == 200

    # Second deletion should fail with 404
    response = client.delete(f'/api/admin/departments/{dept_id}')
    assert response.status_code == 404
    response_data = response.get_json()
    assert response_data['message'] == 'Department not found'


def test_delete_department_concurrent_deletion(client, app):
    """Test handling of concurrent department deletion attempts"""
    with app.app_context():
        # Create a department
        dept = Department(name="concurrent_delete_dept")
        app.db.session.add(dept)
        app.db.session.commit()
        dept_id = dept.id

    # Simulate concurrent deletion requests
    responses = []
    for _ in range(3):
        response = client.delete(f'/api/admin/departments/{dept_id}')
        responses.append(response)

    # One should succeed, others should fail with 404
    success_count = sum(1 for r in responses if r.status_code == 200)
    not_found_count = sum(1 for r in responses if r.status_code == 404)

    assert success_count == 1
    assert not_found_count == 2


def test_delete_department_with_complex_relationships(client, app):
    """Test deleting department with multiple types of relationships"""
    with app.app_context():
        # Create department with various relationships
        dept = Department(name="complex_dept")
        app.db.session.add(dept)
        app.db.session.commit()

        # Add users
        user1 = DepartmentUser(department_id=dept.id, user_handle="user1")
        user2 = DepartmentUser(department_id=dept.id, user_handle="user2")
        app.db.session.add(user1)
        app.db.session.add(user2)

        # Add bearer tokens
        token1 = BearerToken(
            token="complex_token1",
            machine_name="machine1",
            department_id=dept.id,
            created_by="admin"
        )
        token2 = BearerToken(
            token="complex_token2",
            machine_name="machine2",
            department_id=dept.id,
            created_by="admin"
        )
        app.db.session.add(token1)
        app.db.session.add(token2)

        # Add metadata references
        metadata1 = Metadata(
            id="complex_meta1",
            filename="file1.json",
            department_id=dept.id
        )
        metadata2 = Metadata(
            id="complex_meta2",
            filename="file2.json",
            department_id=dept.id
        )
        app.db.session.add(metadata1)
        app.db.session.add(metadata2)

        app.db.session.commit()

        dept_id = dept.id
        user_ids = [user1.id, user2.id]
        token_ids = [token1.id, token2.id]
        metadata_ids = [metadata1.id, metadata2.id]

    response = client.delete(f'/api/admin/departments/{dept_id}')
    assert response.status_code == 200

    # Verify all relationships are handled correctly
    with app.app_context():
        # Department should be deleted
        deleted_dept = app.db.session.get(Department, dept_id)
        assert deleted_dept is None

        # Users should be cascade deleted
        for user_id in user_ids:
            deleted_user = app.db.session.get(DepartmentUser, user_id)
            assert deleted_user is None

        # Bearer tokens should be cascade deactivated
        for token_id in token_ids:
            deleted_token = app.db.session.get(BearerToken, token_id)
            assert deleted_token is not None
            assert deleted_token.is_active is False

        # Metadata should remain and foreign key be nulled
        for metadata_id in metadata_ids:
            remaining_metadata = app.db.session.get(Metadata, metadata_id)
            assert remaining_metadata is not None
            assert remaining_metadata.department_id is None


def test_delete_department_url_encoding(client, app):
    """Test department deletion with URL encoded department ID"""
    with app.app_context():
        dept = Department(name="url_test_dept")
        app.db.session.add(dept)
        app.db.session.commit()
        dept_id = dept.id

    # Test with URL encoded ID (though unnecessary for integers)
    response = client.delete(f'/api/admin/departments/{dept_id}%20')
    # This should result in 404 due to invalid ID format
    assert response.status_code == 404


def test_delete_department_large_id(client):
    """Test deleting department with very large ID"""
    large_id = 999999999999999
    response = client.delete(f'/api/admin/departments/{large_id}')
    assert response.status_code == 404

    response_data = response.get_json()
    assert response_data['message'] == 'Department not found'


def test_delete_department_method_not_allowed(client, bootstrap_department):
    """Test that other HTTP methods are not allowed"""
    dept_id = bootstrap_department.id

    # POST should not be allowed
    response = client.post(f'/api/admin/departments/{dept_id}')
    assert response.status_code == 405

    # PUT should not be allowed
    response = client.put(f'/api/admin/departments/{dept_id}')
    assert response.status_code == 405

    # PATCH should not be allowed
    response = client.patch(f'/api/admin/departments/{dept_id}')
    assert response.status_code == 405
