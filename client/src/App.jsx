import React, { useState } from 'react';
import './App.css';
import UserScreen from './UserScreen';

function App() {
  const [showUserScreen, setShowUserScreen] = useState(false);

  const handleUserClick = () => {
    setShowUserScreen(true);
  };

  const handleBackClick = () => {
    setShowUserScreen(false);
  };

  return (
    <div>
      {!showUserScreen ? (
        <div className="home-screen">
          <h2>Choose your screen:</h2>
          <div className="button-container">
            <button className="button">Admin</button>
            <button className="button" onClick={handleUserClick}>User</button>
          </div>
        </div>
      ) : (
        <UserScreen onBack={handleBackClick} />
      )}
    </div>
  );
}

export default App;
