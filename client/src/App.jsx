import React, { useState } from 'react';
import './App.css';
import UserScreen from './UserScreen';
import AdminLogin from './AdminLogin';
import AdminOverview from './AdminOverview';

function App() {
  const [currentScreen, setCurrentScreen] = useState('home'); // Track the current screen

  const handleUserClick = () => {
    setCurrentScreen('user');
  };

  const handleAdminClick = () => {
    setCurrentScreen('admin-login');
  };

  const handleBackClick = (screen) => {
    setCurrentScreen(screen); // Handle navigation back to specific screens
  };

  return (
    <div>
      {currentScreen === 'home' && (
        <div className="home-screen">
          <h2>Choose your screen:</h2>
          <div className="button-container">
            <button className="button" onClick={handleAdminClick}>Admin</button>
            <button className="button" onClick={handleUserClick}>User</button>
          </div>
        </div>
      )}

      {currentScreen === 'user' && <UserScreen onBack={() => handleBackClick('home')} />}
      {currentScreen === 'admin-login' && <AdminLogin onBack={handleBackClick} />}
      {currentScreen === 'admin-overview' && <AdminOverview />}
    </div>
  );
}

export default App;
