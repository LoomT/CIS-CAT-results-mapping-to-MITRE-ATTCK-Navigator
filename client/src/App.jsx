import React, { useState } from 'react';
import './App.css';

import UserScreen from './UserScreen';
import UserScreenAlt from './UserScreenAlt';
import AdminLogin from './AdminLogin';
import AdminOverview from './AdminOverview';
import HomeScreen from './HomeScreen';
import DemoChoiceScreen from './DemoChoiceScreen';
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
  const [demoChoice, setDemoChoice] = useState(null); // null = start screen
  const [currentScreen, setCurrentScreen] = useState('home'); // used in demo 1 flow
  const [language, setLanguage] = useState('en');
  const t = translations[language];

  // Navigation handlers
  const handleUserClick = () => setCurrentScreen('user');
  const handleAdminClick = () => setCurrentScreen('admin-login');
  const handleBackClick = () => setCurrentScreen('home');

  return (
    <div>
      {/* Language Toggle */}
      <div style={{position: 'absolute', top: 10, right: 120}}>
        <button onClick={() => setLanguage(language === 'en' ? 'nl' : 'en')}>
          {language === 'en' ? 'Nederlands' : 'English'}
        </button>
      </div>

      {/* Render demo choice screen if no choice has been made */}
      {demoChoice === null && (
        <DemoChoiceScreen
          onDemo1Click={() => {
            setDemoChoice('demo1');
            setCurrentScreen('home');
          }}
          onDemo2Click={() => {
            setDemoChoice('demo2');
            setCurrentScreen('user-alt');
          }}
        />
      )}

      {/* Demo 1 flow */}
      {demoChoice === 'demo1' && (
        <>
          {currentScreen === 'home' && (
            <HomeScreen
              onAdminClick={handleAdminClick}
              onUserClick={handleUserClick}
              t={t}
            />
          )}
          {currentScreen === 'admin-login' && (
            <AdminLogin
              onBack={handleBackClick}
              onSuccess={() => setCurrentScreen('admin-overview')}
              t={t}
            />
          )}
          {currentScreen === 'user' && (
            <UserScreen onBack={handleBackClick} t={t}/>
          )}
          {currentScreen === 'admin-overview' && (
            <AdminOverview
              onBack={() => setCurrentScreen('home')}
              t={t}
            />
          )}
        </>
      )}

      {/* Demo 2 flow */}
      {demoChoice === 'demo2' && (
        <>
          {currentScreen === 'user-alt' && (
            <UserScreenAlt
              onBack={() => setDemoChoice(null)}
              onAdminSuccess={() => setCurrentScreen('admin-overview')}
              t={t}
            />
          )}
          {currentScreen === 'admin-overview' && (
            <AdminOverview
              onBack={() => setCurrentScreen('user-alt')}
              t={t}
            />
          )}
        </>
      )}
    </div>
  );
}

export default App;
