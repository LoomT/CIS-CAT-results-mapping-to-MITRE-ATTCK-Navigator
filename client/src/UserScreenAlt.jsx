import React, { useState } from 'react';
import './UserScreen.css';
import './popups.css';

function UserScreenAlt({ onBack, onAdminSuccess, t }) {
  const [showPopup, setShowPopup] = useState(false);
  const [showAdminPopup, setShowAdminPopup] = useState(false);
  const [adminToken, setAdminToken] = useState('');

  const handleVisualizeClick = () => {
    setShowPopup(true);
  };

  const handleClosePopup = () => {
    setShowPopup(false);
  };

  const handleAdminAccess = () => {
    if (adminToken === 'correct-token') {
      setShowAdminPopup(false);
      onAdminSuccess(); // Navigate to admin overview
    } else {
      alert(t.tokenIncorrect || 'Token Incorrect'); // Optional translation
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleAdminAccess();
    }
  };

  return (
    <div className="user-screen">
      {/* Top Navigation Bar */}
      <div className="top-bar">
        <div className="back-text" onClick={onBack}>{t.back}</div>
        <div className="title-text">{t.userOverview}</div>
      </div>

      {/* Side-by-side Content Area */}
      <div className="content-area">
        <div className="upload-section">
          <h2>{t.uploadFile}</h2>
          <button className="upload-button">{t.uploadFile}</button>

          <h2>{t.runBenchmark}</h2>
          <button className="upload-button">{t.runBenchmark}</button>
        </div>

        <div className="file-table-section">
          <h2>{t.filesList}</h2>
          <table className="file-table">
            <thead>
              <tr>
                <th>{t.name}</th>
                <th>{t.department}</th>
                <th>{t.date}</th>
                <th>{t.actions}</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>File 1</td>
                <td>Department 1</td>
                <td>2025-05-04</td>
                <td>
                  <button className="view-button" onClick={handleVisualizeClick}>{t.visualize}</button>
                  <button className="download-button">{t.download}</button>
                </td>
              </tr>
              <tr>
                <td>File 2</td>
                <td>Department 2</td>
                <td>2025-05-04</td>
                <td>
                  <button className="view-button" onClick={handleVisualizeClick}>{t.visualize}</button>
                  <button className="download-button">{t.download}</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Visualization Popup */}
      {showPopup && (
        <div className="popup-overlay">
          <div className="popup">
            <h3 className="popup-heading">{t.chooseFormat}</h3>
            <div className="popup-buttons">
              <button className="popup-button">SVG</button>
              <button className="popup-button">PNG</button>
              <button className="popup-cancel" onClick={handleClosePopup}>{t.cancel}</button>
            </div>
          </div>
        </div>
      )}

      {/* Admin Access Button */}
      <div style={{ position: 'fixed', bottom: 20, left: 20 }}>
        <button className="admin-button" onClick={() => setShowAdminPopup(true)}>
          Admin
        </button>
      </div>

      {/* Admin Token Popup */}
      {showAdminPopup && (
        <div className="popup-overlay">
          <div className="popup">
            <h3 className="popup-heading">{t.enterToken}</h3>
            <input
              type="password"
              value={adminToken}
              onChange={(e) => setAdminToken(e.target.value)}
              onKeyDown={handleKeyDown}
              className="popup-input"
              placeholder={t.enterToken}
            />
            <div className="popup-buttons">
              <button className="popup-button" onClick={handleAdminAccess}>
                {t.confirm}
              </button>
              <button className="popup-cancel" onClick={() => setShowAdminPopup(false)}>
                {t.cancel}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserScreenAlt;
