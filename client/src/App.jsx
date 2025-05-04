// App.jsx
import React, { useState } from 'react';
import './App.css';
import UserScreen from './UserScreen';
import AdminLogin from './AdminLogin';
import AdminOverview from './AdminOverview';
import HomeScreen from './HomeScreen';  // Import HomeScreen component

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
        <HomeScreen
          onAdminClick={handleAdminClick}
          onUserClick={handleUserClick}
        />
      )}

      {currentScreen === 'user' && <UserScreen onBack={() => handleBackClick('home')} />}
      {currentScreen === 'admin-login' && <AdminLogin onBack={handleBackClick} />}
      {currentScreen === 'admin-overview' && <AdminOverview />}
    </div>
  );
}

export default App;
