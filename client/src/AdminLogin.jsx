import React, { useContext, useState } from 'react';
import './globalstyle.css';
import visualIcon from './assets/visual.png';
import { useNavigate } from 'react-router-dom';
import { LanguageContext } from './main.jsx';

/**
 * AdminLogin Component
 * ---------------------
 * Renders the admin login interface where a user can input a token to gain access
 * to the Admin Overview. Includes basic validation and handles submission with the Enter key.
 */
function AdminLogin() {
  // State for storing the entered token
  const [token, setToken] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [showPassword, setShowPassword] = useState(false); // State to toggle password visibility
  const navigate = useNavigate();
  const t = useContext(LanguageContext);

  /**
   * Updates the token state as the user types.
   * @param {object} e - The input change event.
   */
  const handleTokenChange = (e) => {
    setToken(e.target.value);
  };

  /**
   * Handles token validation. If correct triggers the onSuccess callback.
   * Otherwise, it displays an error message.
   *
   * TODO server-side authentication
   */
  const handleSubmit = () => {
    const placeholderToken = 'correct-token'; // Placeholder token for validation
    if (token === placeholderToken) {
      // Navigate to admin overview when token is correct
      navigate('/admin/overview');
    }
    else {
      setErrorMessage('Token Incorrect');
    }
  };

  /**
   * Enables form submission when the Enter key is pressed.
   * @param {object} e - The keydown event.
   */
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="small-panel" data-testid="login-screen">
      {/* Top Center Title */}
      <div className="user-title" data-testid="admin-login-page-title">
        {t.adminLogin}
      </div>

      {/* Token Input Section */}
      <div className="card padded">
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
