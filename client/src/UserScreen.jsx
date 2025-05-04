import React, { useState } from 'react';
import './UserScreen.css';
import './popups.css';

function UserScreen({ onBack }) {
  const [showPopup, setShowPopup] = useState(false);

  const handleVisualizeClick = () => {
    setShowPopup(true);
  };

  const handleClosePopup = () => {
    setShowPopup(false);
  };

  return (
    <div className="user-screen">

      {/* Top Navigation Bar */}
      <div className="top-bar">
        <div className="back-text" onClick={onBack}>← Back</div>
        <div className="title-text">User Overview</div>
      </div>

      {/* Side-by-side Content Area */}
      <div className="content-area">
        {/* Upload Section */}
        <div className="upload-section">
          <h2>Upload a File</h2>
          <button className="upload-button">Upload File</button>

          {/* Run Benchmark Section */}
          <h2>Run Benchmark</h2>
          <button className="upload-button">Run Benchmark</button> {/* Same styling as Upload File */}
        </div>

        {/* File Table Section */}
        <div className="file-table-section">
          <h2>Files List</h2>
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
