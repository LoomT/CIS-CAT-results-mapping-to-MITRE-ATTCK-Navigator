import React, { useState } from 'react';
import './globalstyle.css';

import UserScreen from './UserScreen';
import AdminLogin from './AdminLogin';
import AdminOverview from './AdminOverview';
import HomeScreen from './HomeScreen';
import translations from './translation-map';

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
  const [language, setLanguage] = useState('en');
  const t = translations[language];

  // Navigation handlers
  const handleUserClick = () => setCurrentScreen('user');
  const handleAdminClick = () => setCurrentScreen('admin-login');
  const handleBackClick = () => setCurrentScreen('home');

  return (
    <div>
      {/* Language Toggle */}
      <div style={{ position: 'absolute', top: 10, right: 120 }}>
        <button onClick={() => setLanguage(language === 'en' ? 'nl' : 'en')}>
          {language === 'en' ? 'Nederlands' : 'English'}
        </button>
      </div>

      {/* Main Navigation Flow */}
      {currentScreen === 'home' && (
        <HomeScreen
          onAdminClick={handleAdminClick}
          onUserClick={handleUserClick}
          t={t}
        />
      )}
      {/* Render the Admin Login screen */}
      {currentScreen === 'admin-login' && (
        <AdminLogin
          onBack={handleBackClick}
          onSuccess={() => setCurrentScreen('admin-overview')}
          t={t}
        />
      )}
      {currentScreen === 'admin-overview' && (
        <AdminOverview
          onBack={handleBackClick}
          t={t}
        />
      )}
      {currentScreen === 'user' && (
        <UserScreen
          onBack={handleBackClick}
          t={t}
        />
      )}
    </div>
  );
}

export default App;
