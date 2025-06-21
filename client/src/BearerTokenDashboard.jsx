import React, { useContext, useEffect, useState } from 'react';
import Select from 'react-select';

/**
 * BearerTokenDashboard Component
 * -----------------------------
 * Provides interface for department admins to manage bearer tokens.
 * Features:
 * - View bearer tokens for accessible departments
 * - Create new bearer tokens with machine names
 * - Revoke existing tokens
 * - Copy token to clipboard (only shown once on creation)
 */

function BearerTokenDashboard() {
  const [tokens, setTokens] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [selectedDepartment, setSelectedDepartment] = useState(null);
  const [newMachineName, setNewMachineName] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });
  const [newlyCreatedToken, setNewlyCreatedToken] = useState(null);
  const [showTokenPopup, setShowTokenPopup] = useState(false);

  useEffect(() => {
    fetchTokens();
  }, []);

  const fetchTokens = async () => {
    try {
      const response = await fetch('/api/admin/bearer-tokens');
      if (response.ok) {
        const data = await response.json();
        setTokens(data.tokens);
        setDepartments(data.departments);

        // Auto-select first department if only one available
        if (data.departments.length === 1 && !selectedDepartment) {
          setSelectedDepartment({
            value: data.departments[0].id,
            label: data.departments[0].name,
          });
        }
      }
      else {
        showMessage('Failed to fetch bearer tokens', 'error');
      }
    }
    catch (error) {
      showMessage('Error fetching bearer tokens', 'error');
    }
  };

  const createToken = async () => {
    if (!selectedDepartment) {
      showMessage('Please select a department', 'error');
      return;
    }

    if (!newMachineName.trim()) {
      showMessage('Machine name cannot be empty', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/admin/bearer-tokens', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          department_id: selectedDepartment.value,
          machine_name: newMachineName.trim(),
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setNewlyCreatedToken(data.token);
        setShowTokenPopup(true);
        setNewMachineName('');
        fetchTokens();
        showMessage('Bearer token created successfully', 'success');
      }
      else {
        const error = await response.json();
        showMessage(error.message || 'Failed to create bearer token', 'error');
      }
    }
    catch (error) {
      showMessage('Error creating bearer token', 'error');
    }
    finally {
      setLoading(false);
    }
  };

  const revokeToken = async (tokenId) => {
    if (!window.confirm('Are you sure you want to revoke this token? This action cannot be undone.')) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`/api/admin/bearer-tokens/${tokenId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        fetchTokens();
        showMessage('Token revoked successfully', 'success');
      }
      else {
        const error = await response.json();
        showMessage(error.message || 'Failed to revoke token', 'error');
      }
    }
    catch (error) {
      showMessage('Error revoking token', 'error');
    }
    finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      showMessage('Token copied to clipboard', 'success');
    }).catch(() => {
      showMessage('Failed to copy token', 'error');
    });
  };

  const showMessage = (text, type) => {
    setMessage({ text, type });
    setTimeout(() => setMessage({ text: '', type: '' }), 5000);
  };

  const departmentOptions = departments.map(dept => ({
    value: dept.id,
    label: dept.name,
  }));

  const filteredTokens = selectedDepartment
    ? tokens.filter(token => token.department.id === selectedDepartment.value)
    : tokens;

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="full-panel">
      {/* Top Title */}
      <div className="user-title">Bearer Token Management</div>

      {/* Message Display */}
      {message.text && (
        <div className={`message ${message.type === 'error' ? 'message-error' : 'message-success'}`}>
          {message.text}
        </div>
      )}

      <div className="content-area">
        {/* Token Management Section */}
        <div className="card admin-side-section padded">
          <h2>Create New Token</h2>

          {/* Department Selection */}
          <div className="section-header">
            <p>Department</p>
            <Select
              value={selectedDepartment}
              onChange={setSelectedDepartment}
              options={departmentOptions}
              placeholder="Select department..."
              className="department-select"
              classNamePrefix="react-select"
              isDisabled={departments.length === 1}
            />
          </div>

          {/* Machine Name Input */}
          <div className="section-header">
            <p>Machine Name</p>
            <div className="input-group">
              <input
                type="text"
                placeholder="e.g., Production Server 1"
                value={newMachineName}
                onChange={e => setNewMachineName(e.target.value)}
                onKeyPress={e => e.key === 'Enter' && createToken()}
              />
              <button
                className="btn-green"
                onClick={createToken}
                disabled={loading || !selectedDepartment || !newMachineName.trim()}
              >
                Generate Token
              </button>
            </div>
          </div>

          <div className="info-box">
            <h3>Usage Instructions</h3>
            <p>Bearer tokens allow automated systems to upload assessment results.</p>
            <p>Configure your .wrapper.env file with:</p>
            <code>
              POST_URL=https://your-domain.com/api/files/
              <br />
              POST_BEARER=your-token-here
            </code>
          </div>
        </div>

        {/* Tokens Table Section */}
        <div className="card file-table-section">
          <h2>Active Bearer Tokens</h2>

          {filteredTokens.length === 0
            ? (
                <div className="no-tokens">
                  <p>No active tokens for the selected department.</p>
                </div>
              )
            : (
                <table className="files-table">
                  <thead>
                    <tr>
                      <th>Machine Name</th>
                      <th>Department</th>
                      <th>Created</th>
                      <th>Last Used</th>
                      <th>Created By</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredTokens.map(token => (
                      <tr key={token.id}>
                        <td>{token.machine_name}</td>
                        <td><div className="department-badge">{token.department.name}</div></td>
                        <td>{formatDate(token.created_at)}</td>
                        <td>{formatDate(token.last_used)}</td>
                        <td>{token.created_by}</td>
                        <td>
                          <button
                            className="btn-red small-btn"
                            onClick={() => revokeToken(token.id)}
                            disabled={loading}
                          >
                            Revoke
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
        </div>
      </div>

      {/* Token Display Popup */}
      {showTokenPopup && newlyCreatedToken && (
        <div className="popup-overlay">
          <div className="popup">
            <h3 className="popup-heading">Bearer Token Created</h3>
            <div className="token-display">
              <p>
                <strong>Important:</strong>
                {' '}
                This token will only be shown once. Please copy it now.
              </p>
              <div className="token-info">
                <p>
                  <strong>Machine:</strong>
                  {' '}
                  {newlyCreatedToken.machine_name}
                </p>
                <p>
                  <strong>Department:</strong>
                  {' '}
                  {departments.find(d => d.id === newlyCreatedToken.department.id)?.name}
                </p>
              </div>
              <div className="token-value">
                <code>{newlyCreatedToken.token}</code>
                <button
                  className="btn-blue small-btn"
                  onClick={() => copyToClipboard(newlyCreatedToken.token)}
                >
                  Copy
                </button>
              </div>
            </div>
            <button
              className="popup-button"
              onClick={() => {
                setShowTokenPopup(false);
                setNewlyCreatedToken(null);
              }}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default BearerTokenDashboard;
