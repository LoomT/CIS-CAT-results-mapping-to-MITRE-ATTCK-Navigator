import React, { useState } from 'react';
import './globalstyle.css';
import visualIcon from './assets/visual.png';
import backIcon from './assets/back.png';

/**
 * AdminLogin Component
 * ---------------------
 * Renders the admin login interface where a user can input a token to gain access
 * to the Admin Overview. Includes basic validation and handles submission with the Enter key.
 *
 * Props:
 *  @param onBack (function): Callback to navigate back to the previous screen (e.g., home).
 *  @param onSuccess (function): Callback triggered when the token is successfully validated.
 *  @param t: the translation mapping
 */
function AdminLogin({ onBack, onSuccess, t }) {
  const [token, setToken] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [showPassword, setShowPassword] = useState(false); // State to toggle password visibility

  const handleTokenChange = (e) => {
    setToken(e.target.value);
  };

  const handleSubmit = () => {
    const placeholderToken = 'correct-token'; // Placeholder token for validation
    if (token === placeholderToken) {
      // Navigate to admin overview when token is correct
      onSuccess(); // Pass 'admin-overview' to navigate to the Admin Overview screen
    }
    else {
      setErrorMessage('Token Incorrect');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="admin-panel" data-testid="login-screen">
      {/* Top Center Title */}
      <div className="user-title" data-testid="admin-login-page-title">
        {t.adminLogin}
      </div>

      <div className="back-button">
        <img
          src={backIcon}
          alt="Back"
          className="back-icon"
          onClick={onBack}
        />
      </div>

      {/* Token Input Section */}
      <div className="card">
        {/* TODO: translation */}
        <h2>Enter Token</h2>
        <div className="password-field-container" data-testid="password-field-container">
          <input
            type={showPassword ? 'text' : 'password'}
            value={token}
            onChange={handleTokenChange}
            onKeyDown={handleKeyDown}
            placeholder={t.enterToken}
            className="password-field"
            data-testid="password-field"
          />
          <img
            src={visualIcon}
            alt="Toggle Password Visibility"
            className="toggle-visibility-icon"
            onClick={togglePasswordVisibility}
          />
        </div>
        {/* TODO: translation */}
        <button className="btn-blue" onClick={handleSubmit}>Enter</button>

        {/* Error Message Display */}
        {errorMessage && <div className="error-message">{errorMessage}</div>}
      </div>
    </div>
  );
}

export default AdminLogin;
