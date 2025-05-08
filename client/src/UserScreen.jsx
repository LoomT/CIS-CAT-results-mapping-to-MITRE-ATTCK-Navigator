import React, { useState } from 'react';
import './UserScreen.css';
import './popups.css';
import backIcon from './assets/back.png';
import downloadIcon from './assets/download.png';
import investigateIcon from './assets/investigate.png';
import visualIcon from './assets/visual.png';

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
    <div className="admin-panel">
      {/* Top Center Title */}
      <div className="user-title">
        {t.userOverview}
      </div>

      <div className="back-button">
        <img
          src={backIcon}
          alt="Back"
          className="back-icon"
          onClick={onBack}
        />
      </div>

      {/* Side-by-side Content Area */}
      <div className="content-area">
        {/* Upload Section */}
        <div className="card upload-section">
          <div className="section-header">
            <h2>{t.uploadFile}</h2>
            {/*TODO: translate*/}
            <p>Upload your files for conversion.</p>
          </div>
          <button className="btn-purple">
            <img src={downloadIcon} alt="upload" className="icon flip-vertical" />
            {t.uploadFile}
          </button>

          <div className="section-header" style={{ marginTop: '2rem' }}>
            <h2>{t.runBenchmark}</h2>
            {/*TODO: translate*/}
            <p>Run the benchmark and automatically convert the resulting CIS-CAT output to MITRE ATT&CK navigator.</p>
          </div>
          <button className="btn-purple">
            <img src={investigateIcon} alt="benchmark" className="icon" />
            {t.runBenchmark}
          </button>
        </div>

        {/* File Table Section */}
        <div className="card file-table-section">
          <div className="section-header">
            <h2>{t.filesList}</h2>
            {/*TODO: translate*/}
            <p>View all uploaded files and available actions. Each file can be downloaded as its raw JSON, or visualised as a PNG or SVG.</p>
          </div>
          <table className="files-table">
            <thead>
              <tr>
                <th>{t.name}</th>
                <th>{t.department}</th>
                <th>{t.size}</th>
                <th>{t.date}</th>
                <th>{t.actions}</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>File 1</td>
                <td>
                  <span className="department-badge department-1">Department 1</span>
                </td>
                <td>2.1 MB</td>
                <td>2025-05-04</td>
                <td>
                  {/*TODO: as the application grows, this should be refactored. Else we have a lot of these duplicated mega code blocks*/}
                  <button className="btn-blue" onClick={handleVisualizeClick}>
                    <img src={visualIcon} alt="visualize" className="icon" />
                    {t.visualize}
                  </button>

                  <button className="btn-green">
                    <img src={downloadIcon} alt="download" className="icon" />
                    {t.download}
                  </button>
                </td>
              </tr>
              <tr>
                <td>File 2</td>
                <td>
                  <span className="department-badge department-2">Department 2</span>
                </td>
                <td>3 MB</td>
                <td>2025-05-04</td>
                <td>
                  <button className="btn-blue" onClick={handleVisualizeClick}>
                    <img src={visualIcon} alt="visualize" className="icon" />
                    {t.visualize}
                  </button>

                  <button className="btn-green">
                    <img src={downloadIcon} alt="download" className="icon" />
                    {t.download}
                  </button>

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
            {/*Buttons in the popup*/}
            <div className="popup-buttons">
              <button className="popup-button">SVG</button>
              <button className="popup-button">PNG</button>
              <button className="popup-cancel" onClick={handleClosePopup}>{t.cancel}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserScreen;
