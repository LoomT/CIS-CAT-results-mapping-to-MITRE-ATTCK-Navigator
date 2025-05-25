import React, { useState } from 'react';
import './AdminLogin.css';
import './popups.css';

/**
 * AdminLogin Component
 * ---------------------
 * Renders the admin login interface where a user can input a token to gain access
 * to the Admin Overview. Includes basic validation and handles submission with the Enter key.
 *
 * Props:
 * - onBack (function): Callback to navigate back to the previous screen (e.g., home).
 * - onSuccess (function): Callback triggered when the token is successfully validated.
 */
function AdminLogin({ onBack, onSuccess }) {
  // State for storing the entered token
  const [token, setToken] = useState('');
  // State for showing error messages
  const [errorMessage, setErrorMessage] = useState('');

  /**
   * Updates the token state as the user types.
   * @param {object} e - The input change event.
   */
  const handleTokenChange = (e) => {
    setToken(e.target.value);
  };

  /**
   * Handles token validation. If correct, triggers the onSuccess callback.
   * Otherwise, displays an error message.
   */
  const handleSubmit = () => {
    const placeholderToken = 'correct-token'; // Placeholder token
    if (token === placeholderToken) {
      // Navigate to admin overview when token is correct
      onSuccess(); // Pass 'admin-overview' to navigate to the Admin Overview screen
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
      handleSubmit(); // Submit when Enter is pressed
    }
  };

  return (
    <div className="admin-login">
      {/* Top Navigation Bar */}
      <div className="top-bar">
        <div className="back-text" onClick={() => onBack('home')}>← Back</div>
        <div className="title-text">Admin Login</div>
      </div>

      {/* Token Input Section */}
      <div className="login-section">
        <h2>Enter Token</h2>
        <input
          type="text"
          value={token}
          onChange={handleTokenChange}
          onKeyDown={handleKeyDown}
          placeholder="Enter your token"
        />
        <button className="submit-button" onClick={handleSubmit}>Submit</button>

        {/* Error Message Display */}
        {errorMessage && <div className="error-message">{errorMessage}</div>}
      </div>
    </div>
  );
}

export default AdminLogin;
