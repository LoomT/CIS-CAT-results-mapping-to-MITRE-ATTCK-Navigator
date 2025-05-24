import React from 'react';
import './globalstyle.css';
import { Link } from 'react-router-dom';

/**
 * HomeScreen Component
 * ---------------------
 * The entry screen of the application where users choose between Admin and User roles.
 *
 * Props:
 *  @param t the translation mapping
 */
function HomeScreen({ t }) {
  return (
    <div className="small-panel">
      <div className="card">
        <h2>{t.chooseScreen}</h2>
        {/* Buttons for role selection */}
        <div className="button-container">
          <Link className="btn-blue" to="/admin">Admin</Link>
          <Link
            className="btn-blue"
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
