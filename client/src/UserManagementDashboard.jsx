import React, { useContext, useEffect, useState } from 'react';
import Select from 'react-select';
import './globalstyle.css';
import { LanguageContext } from './main.jsx';

/**
 * UserManagementDashboard Component
 * --------------------------------
 * Provides interface for super admins to manage department admins.
 * Features:
 * - Create new departments
 * - Add/remove users from departments
 * - View current department assignments
 * - Bulk user management
 */

function UserManagementDashboard() {
  const [departments, setDepartments] = useState([]);
  const [users, setUsers] = useState([]);
  const [selectedDepartment, setSelectedDepartment] = useState(null);
  const [newDepartmentName, setNewDepartmentName] = useState('');
  const [newUserHandle, setNewUserHandle] = useState('');
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });
  const t = useContext(LanguageContext);

  useEffect(() => {
    fetchDepartments();
    fetchUsers();
  }, []);

  const fetchDepartments = async () => {
    try {
      const response = await fetch('/api/admin/departments');
      if (response.ok) {
        const data = await response.json();
        setDepartments(data.departments);
      }
      else {
        showMessage('Failed to fetch departments', 'error');
      }
    }
    catch (error) {
      showMessage('Error fetching departments', 'error');
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await fetch('/api/admin/users');
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users);
      }
      else {
        showMessage('Failed to fetch users', 'error');
      }
    }
    catch (error) {
      showMessage('Error fetching users', 'error');
    }
  };

  const createDepartment = async () => {
    if (!newDepartmentName.trim()) {
      showMessage('Department name cannot be empty', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/admin/departments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newDepartmentName.trim(),
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setDepartments([...departments, data.department]);
        setNewDepartmentName('');
        showMessage('Department created successfully', 'success');
      }
      else {
        const error = await response.json();
        showMessage(error.message || 'Failed to create department', 'error');
      }
    }
    catch (error) {
      showMessage('Error creating department', 'error');
    }
    finally {
      setLoading(false);
    }
  };

  const addUserToDepartment = async () => {
    if (!selectedDepartment) {
      showMessage('Please select a department', 'error');
      return;
    }

    if (!newUserHandle.trim()) {
      showMessage('User handle cannot be empty', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/admin/department-users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          department_id: selectedDepartment.value,
          user_handle: newUserHandle.trim(),
        }),
      });

      if (response.ok) {
        setNewUserHandle('');
        fetchUsers();
        showMessage('User added to department successfully', 'success');
      }
      else {
        const error = await response.json();
        showMessage(error.message || 'Failed to add user to department', 'error');
      }
    }
    catch (error) {
      showMessage('Error adding user to department', 'error');
    }
    finally {
      setLoading(false);
    }
  };

  const removeUserFromDepartment = async (userHandle, departmentId) => {
    setLoading(true);
    try {
      const response = await fetch('/api/admin/department-users', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          department_id: departmentId,
          user_handle: userHandle,
        }),
      });

      if (response.ok) {
        fetchUsers();
        showMessage('User removed from department successfully', 'success');
      }
      else {
        const error = await response.json();
        showMessage(error.message || 'Failed to remove user from department', 'error');
      }
    }
    catch (error) {
      showMessage('Error removing user from department', 'error');
    }
    finally {
      setLoading(false);
    }
  };

  const deleteDepartment = async (departmentId) => {
    if (!window.confirm('Are you sure you want to delete this department? This will remove all user assignments.')) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`/api/admin/departments/${departmentId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setDepartments(departments.filter(dept => dept.id !== departmentId));
        fetchUsers();
        showMessage('Department deleted successfully', 'success');
      }
      else {
        const error = await response.json();
        showMessage(error.message || 'Failed to delete department', 'error');
      }
    }
    catch (error) {
      showMessage('Error deleting department', 'error');
    }
    finally {
      setLoading(false);
    }
  };

  const showMessage = (text, type) => {
    setMessage({ text, type });
    setTimeout(() => setMessage({ text: '', type: '' }), 5000);
  };

  const departmentOptions = departments.map(dept => ({
    value: dept.id,
    label: dept.name,
  }));

  const getUsersByDepartment = (departmentId) => {
    return users.filter(user => user.department_id === departmentId);
  };

  return (
    <div className="full-panel">
      {/* Top Title */}
      <div className="user-title">User Management Dashboard</div>

      {/* Message Display */}
      {message.text && (
        <div className={`message ${message.type === 'error' ? 'message-error' : 'message-success'}`}>
          {message.text}
        </div>
      )}

      <div className="content-area">
        {/* Department Management Section */}
        <div className="card admin-side-section">
          <h2>Department Management</h2>

          {/* Create New Department */}
          <div className="section-header">
            <p>Create New Department</p>
            <div className="input-group">
              <input
                type="text"
                placeholder="Department name..."
                value={newDepartmentName}
                onChange={e => setNewDepartmentName(e.target.value)}
                onKeyPress={e => e.key === 'Enter' && createDepartment()}
              />
              <button
                className="btn-blue"
                onClick={createDepartment}
                disabled={loading || !newDepartmentName.trim()}
              >
                Create
              </button>
            </div>
          </div>

          {/* Add User to Department */}
          <div className="section-header">
            <p>Add User to Department</p>
            <Select
              value={selectedDepartment}
              onChange={setSelectedDepartment}
              options={departmentOptions}
              placeholder="Select department..."
              className="department-select"
              classNamePrefix="react-select"
            />
            <div className="input-group">
              <input
                type="text"
                placeholder="User handle..."
                value={newUserHandle}
                onChange={e => setNewUserHandle(e.target.value)}
                onKeyPress={e => e.key === 'Enter' && addUserToDepartment()}
              />
              <button
                className="btn-green"
                onClick={addUserToDepartment}
                disabled={loading || !selectedDepartment || !newUserHandle.trim()}
              >
                Add User
              </button>
            </div>
          </div>
        </div>

        {/* Department Users Cards */}
        <div className="card file-table-section">
          <h2>Current Department Assignments</h2>

          {departments.length === 0
            ? (
                <div className="no-departments">
                  <p>No departments created yet. Create your first department using the form above.</p>
                </div>
              )
            : (
                <div className="departments-grid">
                  {departments.map(department => (
                    <div key={department.id} className="department-card">
                      <div className="department-card-header">
                        <h3>{department.name}</h3>
                        <button
                          className="btn-red small-btn"
                          onClick={() => deleteDepartment(department.id)}
                          disabled={loading}
                          title="Delete Department"
                        >
                          🗑️ Delete
                        </button>
                      </div>

                      <div className="department-users">
                        {getUsersByDepartment(department.id).length === 0
                          ? (
                              <div className="no-users">
                                <em>No users assigned to this department</em>
                              </div>
                            )
                          : (
                              <div className="users-list">
                                {getUsersByDepartment(department.id).map(user => (
                                  <div key={`${department.id}-${user.handle}`} className="user-item">
                                    <div className="user-info">
                                      <span className="user-handle">{user.handle}</span>
                                    </div>
                                    <button
                                      className="btn-red small-btn"
                                      onClick={() => removeUserFromDepartment(user.handle, department.id)}
                                      disabled={loading}
                                      title="Remove user from department"
                                    >
                                      Remove
                                    </button>
                                  </div>
                                ))}
                              </div>
                            )}
                      </div>

                      <div className="department-stats">
                        <small>
                          {getUsersByDepartment(department.id).length}
                          {' '}
                          user
                          {getUsersByDepartment(department.id).length !== 1 ? 's' : ''}
                          {' '}
                          assigned
                        </small>
                      </div>
                    </div>
                  ))}
                </div>
              )}
        </div>
      </div>
    </div>
  );
}

export default UserManagementDashboard;
