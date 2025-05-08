import React, { useState } from 'react';
import './UserScreen.css';
import './popups.css';
import backIcon from './assets/back.png';
import downloadIcon from './assets/download.png';
import visualIcon from './assets/visual.png';

/**
 * AdminOverview Component
 * ------------------------
 * This component renders an administrative view for managing uploaded files.
 * It includes file listings, and actions to visualize, download, and delete files.
 *
 * Props:
 * - onBack (function): Callback triggered when the "Back" button is clicked.
 *
 * State:
 * - showVisualizePopup (boolean): Controls visibility of the visualization format selection popup.
 * - showDeletePopup (boolean): Controls visibility of the delete confirmation popup.
 * - fileToDelete (string|null): Holds the name of the file selected for deletion.
 */

function AdminOverview({ onBack, t }) {
  // Visualization popup visibility
  const [showVisualizePopup, setShowVisualizePopup] = useState(false);
  // Delete confirmation popup visibility
  const [showDeletePopup, setShowDeletePopup] = useState(false);
  // Stores the file name to be deleted
  const [fileToDelete, setFileToDelete] = useState(null);

  /**
   * Triggers the visualize popup.
   */
  const handleVisualizeClick = () => {
    setShowVisualizePopup(true);
  };

  /**
   * Opens the delete confirmation popup for a specific file.
   * @param {string} fileName - The name of the file to be deleted.
   */
  const handleDeleteClick = (fileName) => {
    setFileToDelete(fileName);
    setShowDeletePopup(true); // Show the delete confirmation popup
  };

  /**
   * Confirms deletion of the selected file.
   * (Currently only shows an alert, replace with real logic.)
   */
  const handleDeleteConfirm = () => {
    alert(`File ${fileToDelete} deleted!`); // Placeholder for delete logic
    setShowDeletePopup(false);
  };

  /**
   * Cancels the delete action and closes the confirmation popup.
   */
  const handleDeleteCancel = () => {
    setShowDeletePopup(false);
  };

  /**
   * Closes the visualize popup.
   */
  const handlePopupClose = () => {
    setShowVisualizePopup(false); // Close the visualize popup
  };

  return (
    <div className="admin-panel">
      {/* Top Center Title */}
      <div className="user-title">
        {t.adminOverview}
      </div>

      <div className="back-button">
        <img
          src={backIcon}
          alt="Back"
          className="back-icon"
          onClick={onBack}
        />
      </div>

      {/* Department Toggle Placeholder */}
      <div className="department-toggle">
        <label htmlFor="departmentFilter">Department Filter:</label>
        <select id="departmentFilter" disabled>
          <option>All Departments</option>
        </select>
      </div>

      {/* File Table Section */}
      <div className="card file-table-section">
        <h2>{t.filesList}</h2>
        <p className="section-description">Description placeholder</p>
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
            {/* Placeholder rows */}
            <tr>
              <td>File 1</td>
              <td>
                <span className="department-badge department-1">Department 1</span>
              </td>
              <td>2.1 MB</td>
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
                <button className="delete-button" onClick={() => handleDeleteClick('File 1')}>{t.delete}</button>
              </td>
            </tr>
            <tr>
              <td>File 2</td>
              <td>
                <span className="department-badge department-2">Department 2</span>
              </td>
              <td>3 TB</td>
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
                <button className="delete-button" onClick={() => handleDeleteClick('File 2')}>{t.delete}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Visualize Popup */}
      {showVisualizePopup && (
        <div className="popup-overlay">
          <div className="popup">
            <h3 className="popup-heading">{t.chooseFormat}</h3>
            <div className="popup-buttons">
              <button className="popup-button">SVG</button>
              <button className="popup-button">PNG</button>
              <button className="popup-cancel" onClick={handlePopupClose}>{t.cancel}</button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Popup */}
      {showDeletePopup && (
        <div className="popup-overlay">
          <div className="popup">
            <h3 className="popup-heading">{t.confirmDelete(fileToDelete)}?</h3>
            <div className="popup-buttons">
              <button className="popup-button" onClick={handleDeleteConfirm}>{t.yes}</button>
              <button className="popup-cancel" onClick={handleDeleteCancel}>{t.cancel}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminOverview;
