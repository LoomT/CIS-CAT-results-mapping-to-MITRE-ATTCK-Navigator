import React, { useContext, useEffect, useState } from 'react';
import Select from 'react-select';
import { LanguageContext } from './main.jsx';

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

  const t = useContext(LanguageContext);

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
        showMessage(t.tokenFailedFetch, 'error');
      }
    }
    catch (error) {
      showMessage(t.errorFetchingTokens, 'error');
    }
  };

  const createToken = async () => {
    if (!selectedDepartment) {
      showMessage(t.selectNoDepartment, 'error');
      return;
    }

    if (!newMachineName.trim()) {
      showMessage(t.machineNameEmpty, 'error');
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
        showMessage(t.tokenCreatedSuccessfully, 'success');
      }
      else {
        const error = await response.json();
        showMessage(error.message || t.tokenFailedToCreate, 'error');
      }
    }
    catch (error) {
      showMessage(t.errorCreatingToken, 'error');
    }
    finally {
      setLoading(false);
    }
  };

  const revokeToken = async (tokenId) => {
    if (!window.confirm(t.tokenRevokeConfirmation)) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`/api/admin/bearer-tokens/${tokenId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        fetchTokens();
        showMessage(t.tokenRevokedSuccessfully, 'success');
      }
      else {
        const error = await response.json();
        showMessage(error.message || t.failedToRevokeToken, 'error');
      }
    }
    catch (error) {
      showMessage(t.errorRevokingToken, 'error');
    }
    finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      showMessage(t.tokenCopied, 'success');
    }).catch(() => {
      showMessage(t.tokenNotCopied, 'error');
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
      <div className="user-title">{t.homeBearerTokenManagement}</div>

      {/* Message Display */}
      {message.text && (
        <div className={`message ${message.type === 'error' ? 'message-error' : 'message-success'}`}>
          {message.text}
        </div>
      )}

      <div className="content-area">
        {/* Token Management Section */}
        <div className="card admin-side-section padded">
          <h2>{t.createNewToken}</h2>

          {/* Department Selection */}
          <div className="section-header">
            <p>{t.department}</p>
            <Select
              value={selectedDepartment}
              onChange={setSelectedDepartment}
              options={departmentOptions}
              placeholder={t.selectDepartmentPlaceholder}
              noOptionsMessage={() => t.noOptions}
              className="department-select"
              classNamePrefix="react-select"
              isDisabled={departments.length === 1}
            />
          </div>

          {/* Machine Name Input */}
          <div className="section-header">
            <p>{t.machineName}</p>
            <div className="input-group">
              <input
                type="text"
                placeholder={t.machineNamePlaceholder}
                value={newMachineName}
                onChange={e => setNewMachineName(e.target.value)}
                onKeyPress={e => e.key === 'Enter' && createToken()}
              />
              <button
                className="btn-green"
                onClick={createToken}
                disabled={loading || !selectedDepartment || !newMachineName.trim()}
              >
                {t.generateToken}
              </button>
            </div>
          </div>

          <div className="info-box">
            <h3>{t.usageInstructions}</h3>
            <p>{t.usageInstructionsP1}</p>
            <p>{t.usageInstructionsP2}</p>
            <code>
              {'POST_URL=https://' + t.fakeURL + '/api/files/'}
              <br />
              {'POST_BEARER=' + t.fakeToken}
            </code>
          </div>
        </div>

        {/* Tokens Table Section */}
        <div className="card file-table-section">
          <h2>{t.activeTokens}</h2>

          {filteredTokens.length === 0
            ? (
                <div className="no-tokens">
                  <p>{t.noActiveTokensForDepartment}</p>
                </div>
              )
            : (
                <table className="files-table">
                  <thead>
                    <tr>
                      <th>{t.machineName}</th>
                      <th>{t.department}</th>
                      <th>{t.createdAt}</th>
                      <th>{t.lastUsed}</th>
                      <th>{t.createdBy}</th>
                      <th>{t.actions}</th>
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
                            {t.revoke}
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
            <h3 className="popup-heading">{t.tokenCreated}</h3>
            <div className="token-display">
              <p>
                <strong>{t.important + ':'}</strong>
                {' '}
                {t.displayMsg}
              </p>
              <div className="token-info">
                <p>
                  <strong>
                    {t.machine + ':'}
                  </strong>
                  {' '}
                  {newlyCreatedToken.machine_name}
                </p>
                <p>
                  <strong>{t.department + ':'}</strong>
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
                  {t.copy}
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
              {t.close}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default BearerTokenDashboard;
