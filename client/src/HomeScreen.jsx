import React from 'react';
import './HomeScreen.css';

function HomeScreen({ onAdminClick, onUserClick }) {
  return (
    <div className="home-screen">
      <h2>Choose your screen</h2>
      <div className="button-container">
        <button className="button" onClick={onAdminClick}>Admin</button>
        <button className="button" onClick={onUserClick}>User</button>
      </div>
    </div>
  );
}

export default HomeScreen;
