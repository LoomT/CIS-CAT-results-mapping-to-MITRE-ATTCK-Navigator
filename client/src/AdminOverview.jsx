import React, { useState } from 'react';
import './globalstyle.css';
import './popups.css';
import backIcon from './assets/back.png';
import FileTableEntry from "./FileTableEntry.jsx";

function AdminOverview({ onBack, t }) {
  const [showVisualizePopup, setShowVisualizePopup] = useState(false);
  const [hostSearch, setHostSearch] = useState('');
  const [files] = useState([]);


  const handleVisualizeClick = () => {
    setShowVisualizePopup(true);
  };

  const handleExportClick = () => {
    setShowVisualizePopup(true);
  };

  const handlePopupClose = () => {
    setShowVisualizePopup(false);
  };

  const handleDownload = async (fileId, fileName) => {
    console.log("downloading file: " + fileId)
    let response;
    try {
      response = await fetch(`/api/files/${fileId}`);
    } catch (error) {
      console.error("Error downloading file:", error);
      if (error.name === "AbortError") {
        alert("Downloading was cancelled. Please try again.");
      } else if (error instanceof TypeError) {
        alert("Network error occurred. Please check your internet connection and try again.");
      } else {
        // Fallback for unknown errors
        alert("Failed to download file. Please try again.");
      }
      return;
    }

    if (!response.ok) {
      console.error("Error downloading file:", response);
      switch (response.status) {
      case 400:
        alert("Invalid file id");
        break;
      case 404:
        alert("File not found");
        break;
      case 500:
        alert("Server error occurred while downloading the file. Please try again later.");
        break;
      default:
        alert(`Download failed: ${response.statusText}. Please try again.`);
      }
      return;
    }

    // Get the converted file from the response
    let file;
    try {
      file = await response.blob();
    } catch (error) {
      if (error instanceof DOMException) {
        console.log("Download was cancelled by the user.")
      } else {
        // Fallback for unknown errors
        console.error("Error accessing or decoding response body:", error);
        alert("Error accessing or decoding response body. Please try again.");
      }
      return;
    }

    // Create a download link for the modified file
    const downloadUrl = window.URL.createObjectURL(file);

    // Create a temporary link and trigger download
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(downloadUrl);
  }

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
                <th>Select</th>
                <th>{t.name}</th>
                <th>{t.department}</th>
                <th>{t.date}</th>
                <th>{t.actions}</th>
              </tr>
            </thead>
            <tbody>
              {/* Map files to table rows*/}
              {files.map((file) => (
                <FileTableEntry
                  key={file.id}
                  filename={file.filename}
                  department={file.department}
                  time={file.time}
                  onVisualize={() => handleVisualizeClick(file)}
                  onExport={() => handleExportClick()}
                  onDownload={() => handleDownload(file.id, file.filename)}
                  t={{visualize: "visualize", download:"download"}}
                  showCheckbox={true}
                />
              ))}
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
    </div>
  );
}

export default AdminOverview;