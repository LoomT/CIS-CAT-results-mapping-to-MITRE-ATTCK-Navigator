import React, { useState } from 'react';
import './App.css';
import UserScreen from './UserScreen';
import AdminLogin from './AdminLogin';
import AdminOverview from './AdminOverview';
import HomeScreen from './HomeScreen';

/**
 * App Component
 * --------------
 * The central component of the application that manages navigation between different
 * screens using internal state.
 *
 * Screens:
 * - 'home': Entry point where the user can choose between admin or user view.
 * - 'user': The user interface for non-admin users.
 * - 'admin-login': A secure entryway for admin token validation.
 * - 'admin-overview': Administrative dashboard with file control actions.
 *
 * State:
 * - currentScreen (string): Tracks the active screen being displayed.
 */
function App() {
  /**
   * Track the current screen
   */
  const [currentScreen, setCurrentScreen] = useState('home');

  /**
   * Navigates to the User screen.
   */
  const handleUserClick = () => {
    setCurrentScreen('user');
  };

  /**
   * Navigates to the Admin Login screen.
   */
  const handleAdminClick = () => {
    setCurrentScreen('admin-login');
  };

  /**
   * Navigates back to the Home screen from any other screen.
   */
  const handleBackClick = () => {
    setCurrentScreen('home'); // Navigate back to home screen
  };

  return (
    <div>
      {/* Render the Home screen */}
      {currentScreen === 'home' && (
        <HomeScreen
          onAdminClick={handleAdminClick}
          onUserClick={handleUserClick}
        />
      )}
      {/* Render the Admin Login screen */}
      {currentScreen === 'admin-login' && (
        <AdminLogin
          onBack={handleBackClick}
          onSuccess={() => setCurrentScreen('admin-overview')}
        />
      )}
      {/* Render the User screen */}
      {currentScreen === 'user' && <UserScreen onBack={handleBackClick} />}
      {/* Render the Admin Overview screen */}
      {currentScreen === 'admin-overview' && <AdminOverview onBack={handleBackClick} />}
    </div>
  );
}

export default App;
