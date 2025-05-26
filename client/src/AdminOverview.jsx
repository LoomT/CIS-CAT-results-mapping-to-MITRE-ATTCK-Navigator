import React, { useState } from 'react';
import './AdminOverview.css';
import './popups.css';

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

function AdminOverview({ onBack }) {
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
    <div className="admin-overview">
      {/* Navigation Bar */}
      <div className="top-bar">
        <div className="back-text" onClick={onBack}>← Back</div>
        <div className="title-text">Admin Overview</div>
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
            {/* Placeholder rows */}
            <tr>
              <td>File 1</td>
              <td>Department 1</td>
              <td>2025-05-04</td>
              <td>
                <button className="view-button" onClick={handleVisualizeClick}>Visualize</button>
                <button className="download-button">Download</button>
                <button className="delete-button" onClick={() => handleDeleteClick('File 1')}>Delete</button>
              </td>
            </tr>
            <tr>
              <td>File 2</td>
              <td>Department 2</td>
              <td>2025-05-04</td>
              <td>
                <button className="view-button" onClick={handleVisualizeClick}>Visualize</button>
                <button className="download-button">Download</button>
                <button className="delete-button" onClick={() => handleDeleteClick('File 2')}>Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Visualize Popup */}
      {showVisualizePopup && (
        <div className="popup-overlay">
          <div className="popup">
            <h3 className="popup-heading">Choose a format to visualize</h3>
            <div className="popup-buttons">
              <button className="popup-button">SVG</button>
              <button className="popup-button">PNG</button>
              <button className="popup-cancel" onClick={handlePopupClose}>Cancel</button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Popup */}
      {showDeletePopup && (
        <div className="popup-overlay">
          <div className="popup">
            <h3 className="popup-heading">
              Are you sure you want to delete
              {fileToDelete}
              ?
            </h3>
            <div className="popup-buttons">
              <button className="popup-button" onClick={handleDeleteConfirm}>Yes</button>
              <button className="popup-cancel" onClick={handleDeleteCancel}>Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminOverview;
