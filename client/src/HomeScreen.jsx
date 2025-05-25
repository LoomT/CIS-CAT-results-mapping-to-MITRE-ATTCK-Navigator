import React from 'react';
import './globalstyle.css';

/**
 * HomeScreen Component
 * ---------------------
 * The entry screen of the application where users choose between Admin and User roles.
 *
 * Props:
 *  @param onAdminClick (function): Callback invoked when the "Admin" button is clicked.
 *  @param onUserClick (function): Callback invoked when the "User" button is clicked.
 *  @param t the translation mapping
 */
function HomeScreen({ onAdminClick, onUserClick, t }) {
  return (
    <div className="home-screen">
      <div className="card">
        <h2 className="screen-title">{t.chooseScreen}</h2>
        {/* Buttons for role selection */}
        <div className="button-container">
          <button className="btn-blue" onClick={onAdminClick}>Admin</button>
          <button
            className="btn-blue"
            data-testid="home-screen-user-button"
            onClick={onUserClick}
          >
            {t.user}
          </button>
        </div>
      </div>
    </div>
  );
}

export default HomeScreen;
