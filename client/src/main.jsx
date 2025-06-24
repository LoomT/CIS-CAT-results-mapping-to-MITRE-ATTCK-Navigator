import React, { createContext, StrictMode, useState, useEffect, useContext } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Route, Routes, useLocation } from 'react-router-dom';
import './index.css';
import UserScreen from './UserScreen.jsx';
import HomeScreen from './HomeScreen.jsx';
import AdminOverview from './AdminOverview.jsx';
import UserManagementDashboard from './UserManagementDashboard.jsx';
import BearerTokenDashboard from './BearerTokenDashboard.jsx';
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
          <TitleUpdater />
          <Routes>
            <Route index element={<HomeScreen />} />
            <Route path="/manual-upload" element={<UserScreen />} />
            <Route path="/admin" element={<AdminOverview />} />
            <Route path="/admin/user-management" element={<UserManagementDashboard />} />
            <Route path="/admin/bearer-token-management" element={<BearerTokenDashboard />} />
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
  const [language, setLanguage] = useState(() => {
    // Load language from localStorage if available, else default to 'en'
    return localStorage.getItem('appLanguage') || 'en';
  });

  useEffect(() => {
    localStorage.setItem('appLanguage', language);
  }, [language]);

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
              {language === 'en' ? 'Dutch' : 'Engels'}
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
  const t = useContext(LanguageContext);

  if (authStatus.loading) {
    return (
      <div className="user-display loading">
        <span>{t.loading}</span>
      </div>
    );
  }

  if (!authStatus.user) {
    return (
      <div className="user-display guest">
        <span>{t.roleGuestUser}</span>
      </div>
    );
  }

  const getRoleDisplay = () => {
    if (authStatus.is_super_admin) return t.roleSuperAdmin;
    if (authStatus.is_department_admin) return t.roleDepartmentAdmin;
    return t.roleUser;
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

function TitleUpdater() {
  const location = useLocation();
  const t = useContext(LanguageContext);

  useEffect(() => {
    const titles = {
      '/': t.titleMapper,
      '/manual-upload': t.titleFileUpload,
      '/admin': t.titleReports,
      '/admin/user-management': t.titleUserDepartmentManagement,
      '/admin/bearer-token-management': t.titleBearerTokenManagement,
    };

    const path = location.pathname;
    document.title = titles[path] || 'CIS-CAT Results Mapper to MITTRE ATT\&CK Navigator';
  }, [location.pathname, t]);

  return null;
}
