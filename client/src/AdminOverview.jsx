import React, { useState } from 'react';
import './AdminOverview.css';
import './popups.css';

function AdminOverview({ onBack }) {
  const [showVisualizePopup, setShowVisualizePopup] = useState(false);
  const [showDeletePopup, setShowDeletePopup] = useState(false);
  const [fileToDelete, setFileToDelete] = useState(null);

  const handleVisualizeClick = () => {
    setShowVisualizePopup(true); // Show the visualize popup
  };

  const handleDeleteClick = (fileName) => {
    setFileToDelete(fileName);
    setShowDeletePopup(true); // Show the delete confirmation popup
  };

  const handleDeleteConfirm = () => {
    alert(`File ${fileToDelete} deleted!`); // Placeholder for delete logic
    setShowDeletePopup(false);
  };

  const handleDeleteCancel = () => {
    setShowDeletePopup(false);
  };

  const handlePopupClose = () => {
    setShowVisualizePopup(false); // Close the visualize popup
  };

  return (
    <div className="admin-overview">
      {/* Top Bar */}
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
            <h3 className="popup-heading">Are you sure you want to delete {fileToDelete}?</h3>
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
