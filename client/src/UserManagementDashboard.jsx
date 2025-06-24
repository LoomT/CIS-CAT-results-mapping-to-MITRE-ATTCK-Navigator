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
        showMessage(t.depFailedFetch, 'error');
      }
    }
    catch (error) {
      showMessage(t.errorFetchingDep, 'error');
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
        showMessage(t.usersFailedFetch, 'error');
      }
    }
    catch (error) {
      showMessage(t.usersFailedFetch, 'error');
    }
  };

  const createDepartment = async () => {
    if (!newDepartmentName.trim()) {
      showMessage(t.depNameCannotBeEmpty, 'error');
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
        showMessage(t.depCreatedSuccessfully, 'success');
      }
      else {
        const error = await response.json();
        showMessage(error.message || t.depFailedCreate, 'error');
      }
    }
    catch (error) {
      showMessage(t.errorCreatingDep, 'error');
    }
    finally {
      setLoading(false);
    }
  };

  const addUserToDepartment = async () => {
    if (!selectedDepartment) {
      showMessage(t.selectNoDepartment, 'error');
      return;
    }

    if (!newUserHandle.trim()) {
      showMessage(t.userHandleEmpty, 'error');
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
        showMessage(t.userAddedToDepSuccess, 'success');
      }
      else {
        const error = await response.json();
        showMessage(error.message || t.userFailedAddToDep, 'error');
      }
    }
    catch (error) {
      showMessage(t.errorAddUserToDep, 'error');
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
        showMessage(t.userRemovedSuccess, 'success');
      }
      else {
        const error = await response.json();
        showMessage(error.message || t.userFailedRemoveFromDep, 'error');
      }
    }
    catch (error) {
      showMessage(t.errorRemovingUserFromDep, 'error');
    }
    finally {
      setLoading(false);
    }
  };

  const deleteDepartment = async (departmentId) => {
    if (!window.confirm(t.depRemovalConfirmation)) {
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
        showMessage(t.depDeletedSuccess, 'success');
      }
      else {
        const error = await response.json();
        showMessage(error.message || depFailedDelete, 'error');
      }
    }
    catch (error) {
      showMessage(t.errorDeletingDep, 'error');
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
    <div
      className="full-panel"
      data-testid="user-management-dashboard"
    >
      {/* Top Title */}
      <div className="user-title">{t.userDepartmentDashboard}</div>

      {/* Message Display */}
      {message.text && (
        <div className={`message ${message.type === 'error' ? 'message-error' : 'message-success'}`}>
          {message.text}
        </div>
      )}

      <div className="content-area">
        {/* Department Management Section */}
        <div className="card admin-side-section padded">
          <h2>{t.departmentManagement}</h2>

          {/* Create New Department */}
          <div className="section-header">
            <p>{t.createNewDep}</p>
            <div className="input-group">
              <input
                type="text"
                placeholder={t.createDepPlaceholder + '...'}
                value={newDepartmentName}
                onChange={e => setNewDepartmentName(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && createDepartment()}
              />
              <button
                className="btn-blue"
                onClick={createDepartment}
                disabled={loading || !newDepartmentName.trim()}
              >
                {t.create}
              </button>
            </div>
          </div>

          {/* Add User to Department */}
          <div className="section-header">
            <p>{t.addUserToDep}</p>
            <Select
              value={selectedDepartment}
              onChange={setSelectedDepartment}
              options={departmentOptions}
              placeholder={t.selectDepartment + '...'}
              noOptionsMessage={() => t.noOptions}
              className="department-select"
              classNamePrefix="react-select"
            />
            <div className="input-group">
              <input
                type="text"
                placeholder={t.userHandle + '...'}
                value={newUserHandle}
                onChange={e => setNewUserHandle(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && addUserToDepartment()}
              />
              <button
                className="btn-green"
                onClick={addUserToDepartment}
                disabled={loading || !selectedDepartment || !newUserHandle.trim()}
              >
                {t.addUser}
              </button>
            </div>
          </div>
        </div>

        {/* Department Users Cards */}
        <div className="card file-table-section padded">
          <h2>{t.currentDepAssignments}</h2>

          {departments.length === 0
            ? (
                <div className="no-departments">
                  <p>{t.noDepMessage}</p>
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
                          title={t.deleteDep}
                        >
                          {'🗑️ ' + t.delete}
                        </button>
                      </div>

                      <div className="department-users">
                        {getUsersByDepartment(department.id).length === 0
                          ? (
                              <div className="no-users">
                                <em>{t.noUsersAtDep}</em>
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
                                      title={t.removeUserFromDep}
                                    >
                                      {t.remove}
                                    </button>
                                  </div>
                                ))}
                              </div>
                            )}
                      </div>

                      <div className="department-stats">
                        <small>
                          {t.usersAssigned(getUsersByDepartment(department.id).length)}
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
