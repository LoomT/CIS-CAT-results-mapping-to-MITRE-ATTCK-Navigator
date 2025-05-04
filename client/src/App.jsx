import React, { useState } from 'react';
import './App.css';
import UserScreen from './UserScreen';

function App() {
    const [showUserScreen, setShowUserScreen] = useState(false);
    const handleUserClick = () => {
    setShowUserScreen(true);  // Show the UserScreen when the User button is clicked
  };

  return (
    <div>
      {!showUserScreen ? (
        // Home Screen (with Admin and User buttons)
        <div className="home-screen">
          <h2>Choose your screen:</h2>
          <div className="button-container">
            <button className="button">Admin</button>
            <button className="button" onClick={handleUserClick}>User</button>
          </div>
        </div>
      ) : (
        // User Screen will be shown when `showUserScreen` is true
        <UserScreen />
      )}
    </div>
  );
}


export default App;
