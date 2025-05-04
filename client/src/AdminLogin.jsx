import React, { useState } from 'react';
import './AdminLogin.css';
import './popups.css';

function AdminLogin({ onBack, onSuccess }) {
  const [token, setToken] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const handleTokenChange = (e) => {
    setToken(e.target.value);
  };

  const handleSubmit = () => {
    const placeholderToken = 'correct-token'; // Placeholder token
    if (token === placeholderToken) {
      // Navigate to admin overview when token is correct
      onSuccess(); // Pass 'admin-overview' to navigate to the Admin Overview screen
    } else {
      setErrorMessage('Token Incorrect');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSubmit(); // Submit when Enter is pressed
    }
  };

  return (
    <div className="admin-login">
      <div className="top-bar">
        <div className="back-text" onClick={() => onBack('home')}>← Back</div>
        <div className="title-text">Admin Login</div>
      </div>

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

        {errorMessage && <div className="error-message">{errorMessage}</div>}
      </div>
    </div>
  );
}

export default AdminLogin;
