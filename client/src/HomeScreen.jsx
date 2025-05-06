import React from 'react';
import './HomeScreen.css';

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
      <h2>Choose your screen</h2>
      {/* Buttons for role selection */}
      <div className="button-container">
        <button className="button" onClick={onAdminClick}>Admin</button>
        <button className="button" onClick={onUserClick}>User</button>
      </div>
    </div>
  );
}

export default HomeScreen;
