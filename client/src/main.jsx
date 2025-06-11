import React, { createContext, StrictMode, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import './index.css';
import UserScreen from './UserScreen.jsx';
import HomeScreen from './HomeScreen.jsx';
import AdminLogin from './AdminLogin.jsx';
import AdminOverview from './AdminOverview.jsx';
import UserManagementDashboard from './UserManagementDashboard.jsx';
import translations from './translation-map';

export const LanguageContext = createContext(translations['en']);

/**
 * Main Component
 * --------------
 * The central component of the application that manages navigation between different
 * screens using internal state.
 */
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <LanguageProvider>
      <BrowserRouter>
        <Routes>
          <Route index element={<HomeScreen />} />
          <Route path="/manual-conversion" element={<UserScreen />} />
          <Route path="/admin" element={<AdminLogin />} />
          <Route path="/admin/overview" element={<AdminOverview />} />
          <Route path="/admin/user-management" element={<UserManagementDashboard />} />
        </Routes>
      </BrowserRouter>
    </LanguageProvider>
  </StrictMode>,
);

function LanguageProvider({ children }) {
  const [language, setLanguage] = useState('en');
  return (
    <LanguageContext.Provider value={translations[language]}>
      <div id="main-content" className="full-panel">
        {/* Language Toggle */}
        <nav>
          <button onClick={() => setLanguage(language === 'en' ? 'nl' : 'en')}>
            {language === 'en' ? 'Nederlands' : 'English'}
          </button>
        </nav>
        {children}
      </div>
    </LanguageContext.Provider>
  );
}
