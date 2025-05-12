import React from 'react';
import './globalstyle.css';

/**
 * HomeScreen Component
 * ---------------------
 * The entry screen of the application where users choose between Admin and User roles.
 *
 * Props:
 * - onAdminClick (function): Callback invoked when the "Admin" button is clicked.
 * - onUserClick (function): Callback invoked when the "User" button is clicked.
 */
function HomeScreen({ onAdminClick, onUserClick }) {
  return (
    <div className="home-screen">
      <div className="card">
        <h2 className="screen-title">Choose your screen</h2>
        {/* Buttons for role selection */}
        <div className="button-container">
          <button className="btn-blue" onClick={onAdminClick}>Admin</button>
          <button className="btn-blue" onClick={onUserClick}>User</button>
        </div>
      </div>
    </div>
  );
}

export default HomeScreen;
