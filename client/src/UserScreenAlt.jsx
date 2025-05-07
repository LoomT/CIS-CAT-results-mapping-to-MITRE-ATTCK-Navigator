import React, { useState } from 'react';
import './UserScreenAlt.css';
import './popups.css';

/**
 * UserScreen Component
 * ---------------------
 * Provides the main interface for regular users. Includes:
 * - File upload and benchmarking actions (currently placeholders).
 * - A list of files with actions for visualization and download.
 * - A popup modal for choosing visualization formats.
 *
 * Props:
 * - onBack (function): Callback to navigate back to the previous screen (typically home).
 */

function UserScreen({ onBack, t }) {
  const [showPopup, setShowPopup] = useState(false);

  /**
   * Opens the visualization popup.
   */
  const handleVisualizeClick = () => {
    setShowPopup(true);
  };

  /**
   * Closes the visualization popup.
   */
  const handleClosePopup = () => {
    setShowPopup(false);
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
        {/* Upload Section */}
        <div className="upload-section">
          <h2>{t.uploadFile}</h2>
          <button className="upload-button">{t.uploadFile}</button>

          {/* Run Benchmark Section */}
          <h2>{t.runBenchmark}</h2>
          <button className="upload-button">{t.runBenchmark}</button> {/* Same styling as Upload File */}
        </div>

        {/* File Table Section */}
        <div className="file-table-section">
          <h2>{t.filesList}</h2>
          <table className="file-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Department</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>File 1</td>
                <td>Department 1</td>
                <td>2025-05-04</td>
                <td>
                  <button className="view-button" onClick={handleVisualizeClick}>Visualize</button>
                  <button className="download-button">Download</button>
                </td>
              </tr>
              <tr>
                <td>File 2</td>
                <td>Department 2</td>
                <td>2025-05-04</td>
                <td>
                  <button className="view-button" onClick={handleVisualizeClick}>Visualize</button>
                  <button className="download-button">Download</button>
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
            <h3 className="popup-heading">Choose a format to visualize</h3>
            {/*Buttons in the popup*/}
            <div className="popup-buttons">
              <button className="popup-button">SVG</button>
              <button className="popup-button">PNG</button>
              <button className="popup-cancel" onClick={handleClosePopup}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserScreen;
