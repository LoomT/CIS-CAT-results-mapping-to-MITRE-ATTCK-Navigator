import React, { useContext } from 'react';
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
  return (
    <div className="small-panel">
      <div className="card">
        <h2>{t.chooseScreen}</h2>
        {/* Buttons for role selection */}
        <div className="button-container">
          <Link
            className="button btn-blue"
            data-testid="home-screen-admin-button"
            to="/admin"
          >
            Admin
          </Link>
          <Link
            className="button btn-blue"
            data-testid="home-screen-admin-button"
            to="/admin/user-management"
          >
            Admin Dashboard
          </Link>
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
