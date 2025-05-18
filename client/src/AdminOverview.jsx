import React, { useState } from 'react';
import './globalstyle.css';
import './popups.css';
import backIcon from './assets/back.png';
import downloadIcon from './assets/download.png';
import visualIcon from './assets/visual.png';

function AdminOverview({ onBack, t }) {
  const [showVisualizePopup, setShowVisualizePopup] = useState(false);
  const [showDeletePopup, setShowDeletePopup] = useState(false);
  const [fileToDelete, setFileToDelete] = useState(null);
  const [hostSearch, setHostSearch] = useState('');

  const handleVisualizeClick = () => {
    setShowVisualizePopup(true);
  };

  const handleDeleteClick = (fileName) => {
    setFileToDelete(fileName);
    setShowDeletePopup(true);
  };

  const handleDeleteConfirm = () => {
    alert(`File ${fileToDelete} deleted!`);
    setShowDeletePopup(false);
  };

  const handleDeleteCancel = () => {
    setShowDeletePopup(false);
  };

  const handlePopupClose = () => {
    setShowVisualizePopup(false);
  };

  return (
    <div className="admin-panel">
      {/* Top Title */}
      <div className="user-title">{t.adminOverview}</div>

      <div className="back-button">
        <img src={backIcon} alt="Back" className="back-icon" onClick={onBack} />
      </div>

      {/* New Cards Section */}
      <div className="content-area">
        <div className="card">
          <div className="section-header">
            <h2>{t.departmentFilter}</h2>
            <select id="departmentFilter">
              <option>All Departments</option>
              <option>Department 1</option>
              <option>Department 2</option>
            </select>
          </div>

          <div className="section-header">
            <h2>{t.searchHosts}</h2>
            <input
              type="text"
              placeholder="Search hosts..."
              value={hostSearch}
              onChange={(e) => setHostSearch(e.target.value)}
            />
          </div>
        </div>


        {/* File Table Section */}
        <div className="card file-table-section">
          <h2>{t.filesList}</h2>
          <p className="section-description">Description placeholder</p>
          <table className="files-table">
            <thead>
              <tr>
                <th>{t.select}</th>
                <th>{t.name}</th>
                <th>{t.department}</th>
                <th>{t.size}</th>
                <th>{t.date}</th>
                <th>{t.actions}</th>
              </tr>
            </thead>
            <tbody>
              {/* Example Row */}
              <tr>
                <td>
                  <button className="square-button">☐</button>
                </td>
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
                  <button className="delete-button" onClick={() => handleDeleteClick('File 1')}>
                    {t.delete}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Popups */}
      {showVisualizePopup && (
        <div className="popup-overlay">
          <div className="popup">
            <h3 className="popup-heading">{t.chooseFormat}</h3>
            <div className="popup-buttons">
              <button className="popup-button">SVG</button>
              <button className="popup-button">PNG</button>
              <button className="popup-cancel" onClick={handlePopupClose}>
                {t.cancel}
              </button>
            </div>
          </div>
        </div>
      )}

      {showDeletePopup && (
        <div className="popup-overlay">
          <div className="popup">
            <h3 className="popup-heading">{t.confirmDelete(fileToDelete)}?</h3>
            <div className="popup-buttons">
              <button className="popup-button" onClick={handleDeleteConfirm}>
                {t.yes}
              </button>
              <button className="popup-cancel" onClick={handleDeleteCancel}>
                {t.cancel}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminOverview;