import React, { useContext, useState, useEffect } from 'react';
import './globalstyle.css';
import { Link } from 'react-router-dom';
import { LanguageContext } from './main.jsx';

/**
 * HomeScreen Component
 * ---------------------
 * The entry screen of the application where users choose between Admin and User roles.
 */
function HomeScreen() {
  const t = useContext(LanguageContext);
  const [authStatus, setAuthStatus] = useState({
    user: null,
    is_super_admin: false,
    is_department_admin: false,
    loading: true,
  });

  useEffect(() => {
    fetchAuthStatus();
  }, []);

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
        // If auth status fails, assume no permissions
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

  // Show loading state while checking permissions
  if (authStatus.loading) {
    return (
      <div className="small-panel">
        <div className="card">
          <h2>Loading...</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="small-panel">
      <div className="card">
        <h2>{t.chooseScreen}</h2>
        {/* Buttons for role selection - shown based on permissions */}
        <div className="button-container">
          {/* Admin button - shown if user is department admin or super admin */}
          {(authStatus.is_department_admin || authStatus.is_super_admin) && (
            <Link
              className="button btn-blue"
              data-testid="home-screen-admin-button"
              to="/admin"
            >
              Admin
            </Link>
          )}

          {/* User Management button - shown only if user is super admin */}
          {authStatus.is_super_admin && (
            <Link
              className="button btn-blue"
              data-testid="home-screen-admin-user-management"
              to="/admin/user-management"
            >
              User Management
            </Link>
          )}

          {/* User/Manual Conversion button - always shown for all users */}
          <Link
            className="button btn-blue"
            data-testid="home-screen-user-button"
            to="/manual-conversion"
          >
            {t.user}
          </Link>
        </div>
      </div>
    </div>
  );
}

export default HomeScreen;
