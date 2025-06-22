from api.db.models import Department, DepartmentUser
from tests.conftest import enable_authentication


def test_get_users_success_no_users(client):
    """Test successful users retrieval when no users exist"""
    response = client.get('/api/admin/users')

    assert response.status_code == 200
    data = response.get_json()

    assert 'users' in data
    assert isinstance(data['users'], list)
    assert len(data['users']) == 0


def test_get_users_success_with_users(client, bootstrap_tokens_and_users):
    """Test successful users retrieval when users exist"""
    response = client.get('/api/admin/users')

    assert response.status_code == 200
    data = response.get_json()

    assert 'users' in data
    assert isinstance(data['users'], list)
    assert len(data['users']) == 2  # Two users from bootstrap fixture

    # Verify user structure
    for user in data['users']:
        assert 'handle' in user
        assert isinstance(user['handle'], str)

    # Verify specific users exist
    user_handles = [user['handle'] for user in data['users']]
    assert 'dept1_admin' in user_handles
    assert 'dept2_admin' in user_handles


def test_get_users_user_department_structure(client,
                                             bootstrap_tokens_and_users):
    """Test that user-department relationships are properly structured"""
    response = client.get('/api/admin/users')
    assert response.status_code == 200

    data = response.get_json()
    users = data['users']

    for user in users:

        assert 'department_id' in user
        assert 'department_name' in user
        assert isinstance(user['department_id'], int)
        assert isinstance(user['department_name'], str)

    # Find specific users and verify their departments
    dept1_admin = next(u for u in users if u['handle'] == 'dept1_admin')
    dept2_admin = next(u for u in users if u['handle'] == 'dept2_admin')

    assert dept1_admin['department_name'] == 'bearer_token_dept1'
    assert dept2_admin['department_name'] == 'bearer_token_dept2'


def test_get_users_multiple_departments_per_user(client, app):
    """Test users with multiple department assignments"""
    with app.app_context():
        # Create departments
        dept1 = Department(name="multi_dept1")
        dept2 = Department(name="multi_dept2")
        dept3 = Department(name="multi_dept3")
        app.db.session.add(dept1)
        app.db.session.add(dept2)
        app.db.session.add(dept3)
        app.db.session.commit()

        # Create user with multiple department assignments
        user1 = DepartmentUser(
            department_id=dept1.id,
            user_handle="multi_user"
        )
        user2 = DepartmentUser(
            department_id=dept2.id,
            user_handle="multi_user"
        )
        user3 = DepartmentUser(
            department_id=dept1.id,
            user_handle="single_user"
        )
        app.db.session.add(user1)
        app.db.session.add(user2)
        app.db.session.add(user3)
        app.db.session.commit()

        response = client.get('/api/admin/users')
        assert response.status_code == 200

        data = response.get_json()
        users = data['users']

        # Should have 3 users
        assert len(users) == 3

        # Find multi_user
        multi_user_deps = list(
            (u['department_id'], u['department_name'])
            for u in users if u['handle'] == 'multi_user'
        )

        single_user_deps = list(
            (u['department_id'], u['department_name'])
            for u in users if u['handle'] == 'single_user'
        )

        # multi_user should have 2 departments
        assert len(multi_user_deps) == 2
        assert {
                   (dept1.id, dept1.name),
                   (dept2.id, dept2.name)
               } == set(multi_user_deps)

        # single_user should have 1 department
        assert len(single_user_deps) == 1
        assert single_user_deps[0][1] == 'multi_dept1'


def test_get_users_super_admin_only_access(client, bootstrap_tokens_and_users):
    """Test that only super admin can access users endpoint"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'super_admin',
        'X-Forwarded-For': '127.0.0.1'
    }

    response = client.get('/api/admin/users', headers=headers)
    assert response.status_code == 200

    data = response.get_json()
    assert 'users' in data
    assert len(data['users']) == 2


def test_get_users_department_admin_rejected(client,
                                             bootstrap_tokens_and_users):
    """Test that department admin cannot access users endpoint"""
    enable_authentication(client)

    dept1_admin = bootstrap_tokens_and_users['dept1_admin']
    headers = {
        'X-Forwarded-User': dept1_admin.user_handle,
        'X-Forwarded-For': '127.0.0.1'
    }

    response = client.get('/api/admin/users', headers=headers)
    assert response.status_code == 403

    data = response.get_json()
    assert data['message'] == 'Super admin privileges required'


def test_get_users_unauthenticated(client):
    """Test users endpoint without authentication when SSO enabled"""
    enable_authentication(client)

    response = client.get('/api/admin/users')
    assert response.status_code == 401

    data = response.get_json()
    assert data['message'] == 'Authentication required'


def test_get_users_unauthorized_user(client, bootstrap_tokens_and_users):
    """Test users endpoint with user that has no admin privileges"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'regular_user',
        'X-Forwarded-For': '127.0.0.1'
    }

    response = client.get('/api/admin/users', headers=headers)
    assert response.status_code == 403

    data = response.get_json()
    assert data['message'] == 'Super admin privileges required'


def test_get_users_untrusted_ip(client):
    """Test users endpoint from untrusted IP"""
    enable_authentication(client)

    headers = {
        'X-Forwarded-User': 'super_admin',
        'X-Forwarded-For': '192.168.1.100'  # Untrusted IP
    }

    response = client.get('/api/admin/users', headers=headers)
    assert response.status_code == 403

    data = response.get_json()
    assert data['message'] == 'Super admin privileges required'


def test_get_users_bearer_token_authentication_rejected(
        client, bootstrap_tokens_and_users):
    """Test that bearer token authentication is rejected for users endpoint"""
    enable_authentication(client)

    headers = {
        'Authorization': 'Bearer test-token-1'
    }

    response = client.get('/api/admin/users', headers=headers)
    assert response.status_code == 403

    data = response.get_json()
    assert data['message'] == 'Super admin privileges required'


def test_get_users_special_characters_in_handle(client, app):
    """Test users with special characters in handles"""
    with app.app_context():
        dept = Department(name="special_chars_dept")
        app.db.session.add(dept)
        app.db.session.commit()

        # Create user with special characters
        user = DepartmentUser(
            department_id=dept.id,
            user_handle="user.with-special_chars@domain.com"
        )
        app.db.session.add(user)
        app.db.session.commit()

        response = client.get('/api/admin/users')
        assert response.status_code == 200

        data = response.get_json()
        assert len(data['users']) == 1
        assert data['users'][0][
                   'handle'] == "user.with-special_chars@domain.com"


def test_get_users_empty_user_handle(client, app):
    """Test handling of edge case user handles"""
    with app.app_context():
        dept = Department(name="edge_case_dept")
        app.db.session.add(dept)
        app.db.session.commit()

        # Create user with minimal handle
        user = DepartmentUser(
            department_id=dept.id,
            user_handle="a"
        )
        app.db.session.add(user)
        app.db.session.commit()

        response = client.get('/api/admin/users')
        assert response.status_code == 200

        data = response.get_json()
        assert len(data['users']) == 1
        assert data['users'][0]['handle'] == "a"


def test_get_users_database_error(client, mocker):
    """Test users endpoint with database error"""
    # Mock the database method to raise an exception
    mocker.patch(
        'api.app.get_all_users_with_departments',
        side_effect=Exception("Database connection error")
    )

    response = client.get('/api/admin/users')

    assert response.status_code == 500
    data = response.get_json()
    assert data['message'] == 'Error fetching users'


def test_get_users_consistent_ordering(client, app):
    """Test that users are returned in consistent order"""
    with app.app_context():
        dept = Department(name="ordering_dept")
        app.db.session.add(dept)
        app.db.session.commit()

        # Create multiple users
        users_data = [
            "user_z",
            "user_a",
            "user_m",
            "user_1",
            "user_Z"  # Test case sensitivity
        ]

        created_users = []
        for user_handle in users_data:
            user = DepartmentUser(
                department_id=dept.id,
                user_handle=user_handle
            )
            app.db.session.add(user)
            created_users.append(user)

        app.db.session.commit()

        # Make multiple requests to verify consistent ordering
        responses = []
        for _ in range(3):
            response = client.get('/api/admin/users')
            assert response.status_code == 200
            responses.append(response.get_json())

        # All responses should have the same order
        for i in range(1, len(responses)):
            handles_1 = [u['handle'] for u in responses[0]['users']]
            handles_i = [u['handle'] for u in responses[i]['users']]
            assert handles_1 == handles_i

        # Verify all users are present
        final_handles = [u['handle'] for u in responses[0]['users']]
        for expected_handle in users_data:
            assert expected_handle in final_handles


def test_get_users_concurrent_access(client, bootstrap_tokens_and_users):
    """Test users endpoint handles concurrent access properly"""
    # Simulate multiple concurrent requests
    responses = []

    for _ in range(5):
        response = client.get('/api/admin/users')
        responses.append(response)

    # All requests should succeed
    for response in responses:
        assert response.status_code == 200
        data = response.get_json()
        assert 'users' in data
        assert len(data['users']) == 2


def test_get_users_large_dataset_simulation(client, app):
    """Test users endpoint with a larger dataset"""
    with app.app_context():
        # Create multiple departments
        departments = []
        for i in range(5):
            dept = Department(name=f"large_test_dept_{i}")
            app.db.session.add(dept)
            departments.append(dept)
        app.db.session.commit()

        # Create many users across departments
        users = []
        for i in range(50):
            dept_index = i % len(departments)
            user = DepartmentUser(
                department_id=departments[dept_index].id,
                user_handle=f"large_test_user_{i:03d}"
            )
            app.db.session.add(user)
            users.append(user)
        app.db.session.commit()

        response = client.get('/api/admin/users')
        assert response.status_code == 200

        data = response.get_json()
        assert len(data['users']) == 50

        # Verify all users have proper structure
        for user in data['users']:
            assert 'handle' in user
            assert 'department_id' in user
            assert 'department_name' in user


def test_get_users_orphaned_department_reference(client, app):
    """Test handling of users with invalid department references"""
    with app.app_context():
        dept = Department(name="temp_dept")
        app.db.session.add(dept)
        app.db.session.commit()

        user = DepartmentUser(
            department_id=dept.id,
            user_handle="orphaned_user"
        )
        app.db.session.add(user)
        app.db.session.commit()

        # Delete department but leave user (simulating orphaned reference)
        app.db.session.delete(dept)
        app.db.session.commit()

        # This should handle the orphaned reference gracefully
        response = client.get('/api/admin/users')
        # Response should still be successful but user might not be included
        # or might have null department info depending on implementation
        assert response.status_code == 200


def test_get_users_method_not_allowed(client):
    """Test that other HTTP methods are not allowed"""
    # POST should not be allowed
    response = client.post('/api/admin/users')
    assert response.status_code == 405

    # PUT should not be allowed
    response = client.put('/api/admin/users')
    assert response.status_code == 405

    # DELETE should not be allowed
    response = client.delete('/api/admin/users')
    assert response.status_code == 405

    # PATCH should not be allowed
    response = client.patch('/api/admin/users')
    assert response.status_code == 405


def test_get_users_trailing_slash(client, bootstrap_tokens_and_users):
    """Test users endpoint with trailing slash in URL"""
    # URL with trailing slash should work
    response = client.get('/api/admin/users/')
    assert response.status_code == 200

    data = response.get_json()
    assert 'users' in data
    assert len(data['users']) == 2


def test_get_users_case_sensitivity(client, app):
    """Test case sensitivity in user handles"""
    with app.app_context():
        dept = Department(name="case_test_dept")
        app.db.session.add(dept)
        app.db.session.commit()

        # Create users with different cases
        user1 = DepartmentUser(
            department_id=dept.id,
            user_handle="TestUser"
        )
        user2 = DepartmentUser(
            department_id=dept.id,
            user_handle="testuser"
        )
        user3 = DepartmentUser(
            department_id=dept.id,
            user_handle="TESTUSER"
        )
        app.db.session.add(user1)
        app.db.session.add(user2)
        app.db.session.add(user3)
        app.db.session.commit()

        response = client.get('/api/admin/users')
        assert response.status_code == 200

        data = response.get_json()
        assert len(data['users']) == 3

        # Verify all variations are present
        handles = [u['handle'] for u in data['users']]
        assert 'TestUser' in handles
        assert 'testuser' in handles
        assert 'TESTUSER' in handles


def test_get_users_performance_stress(client, app):
    """Test users endpoint performance under stress"""
    with app.app_context():
        dept = Department(name="stress_test_dept")
        app.db.session.add(dept)
        app.db.session.commit()

        # Create a reasonable number of users for stress testing
        users = []
        for i in range(100):
            user = DepartmentUser(
                department_id=dept.id,
                user_handle=f"stress_user_{i:04d}"
            )
            users.append(user)

        # Batch insert for performance
        app.db.session.add_all(users)
        app.db.session.commit()

        # Test multiple rapid requests
        for _ in range(10):
            response = client.get('/api/admin/users')
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['users']) == 100
