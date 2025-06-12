import React, { createContext, StrictMode, useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import './index.css';
import UserScreen from './UserScreen.jsx';
import HomeScreen from './HomeScreen.jsx';
import AdminOverview from './AdminOverview.jsx';
import UserManagementDashboard from './UserManagementDashboard.jsx';
import translations from './translation-map';

export const LanguageContext = createContext(translations['en']);
export const AuthContext = createContext({
  user: null,
  is_super_admin: false,
  is_department_admin: false,
  loading: true,
  refreshAuth: () => {},
});

/**
 * Main Component
 * --------------
 * The central component of the application that manages navigation between different
 * screens using internal state.
 */
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <LanguageProvider>
        <BrowserRouter>
          <Routes>
            <Route index element={<HomeScreen />} />
            <Route path="/manual-conversion" element={<UserScreen />} />
            <Route path="/admin" element={<AdminOverview />} />
            <Route path="/admin/user-management" element={<UserManagementDashboard />} />
          </Routes>
        </BrowserRouter>
      </LanguageProvider>
    </AuthProvider>
  </StrictMode>,
);

function AuthProvider({ children }) {
  const [authStatus, setAuthStatus] = useState({
    user: null,
    is_super_admin: false,
    is_department_admin: false,
    loading: true,
  });

  const fetchAuthStatus = async () => {
    try {
      const response = await fetch('/api/auth/status');
      if (response.ok) {
        const data = await response.json();
        setAuthStatus({
          user: data.user,
          is_super_admin: data.is_super_admin,
          is_department_admin: data.is_department_admin,
          loading: false,
        });
      }
      else {
        setAuthStatus({
          user: null,
          is_super_admin: false,
          is_department_admin: false,
          loading: false,
        });
      }
    }
    catch (error) {
      console.error('Error fetching auth status:', error);
      setAuthStatus({
        user: null,
        is_super_admin: false,
        is_department_admin: false,
        loading: false,
      });
    }
  };

  useEffect(() => {
    fetchAuthStatus();
  }, []);

  const refreshAuth = () => {
    fetchAuthStatus();
  };

  return (
    <AuthContext.Provider value={{
      ...authStatus,
      refreshAuth,
    }}
    >
      {children}
    </AuthContext.Provider>
  );
}

function LanguageProvider({ children }) {
  const [language, setLanguage] = useState('en');
  return (
    <LanguageContext.Provider value={translations[language]}>
      <div id="main-content" className="full-panel">
        <nav>
          <div className="nav-left">
            <UserDisplay />
          </div>
          <div className="nav-center" />
          {/* Language Toggle */}
          <div className="nav-right">
            <button onClick={() => setLanguage(language === 'en' ? 'nl' : 'en')}>
              {language === 'en' ? 'Nederlands' : 'English'}
            </button>
          </div>
        </nav>
        {children}
      </div>
    </LanguageContext.Provider>
  );
}

function UserDisplay() {
  const authStatus = React.useContext(AuthContext);

  if (authStatus.loading) {
    return (
      <div className="user-display loading">
        <span>Loading...</span>
      </div>
    );
  }

  if (!authStatus.user) {
    return (
      <div className="user-display guest">
        <span>Guest User</span>
      </div>
    );
  }

  const getRoleDisplay = () => {
    if (authStatus.is_super_admin) return 'Super Admin';
    if (authStatus.is_department_admin) return 'Department Admin';
    return 'User';
  };

  return (
    <div className="user-display authenticated">
      <div className="user-info">
        <span className="user-name">{authStatus.user}</span>
        <span className="user-role">{getRoleDisplay()}</span>
      </div>
    </div>
  );
}
