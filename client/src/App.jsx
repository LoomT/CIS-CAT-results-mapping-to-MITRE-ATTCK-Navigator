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

  const handleBackClick = () => {
    setCurrentScreen('home'); // Navigate back to home screen
  };

  return (
    <div>
      {currentScreen === 'home' && (
        <HomeScreen
          onAdminClick={handleAdminClick}
          onUserClick={handleUserClick}
        />
      )}

   {currentScreen === 'admin-login' && (
  <AdminLogin
    onBack={handleBackClick}
    onSuccess={() => setCurrentScreen('admin-overview')}
  />
)}


      {currentScreen === 'user' && <UserScreen onBack={handleBackClick} />}
      {currentScreen === 'admin-overview' && <AdminOverview onBack={handleBackClick} />}
    </div>
  );
}

export default App;
