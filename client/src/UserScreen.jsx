import React, {useCallback, useState} from 'react';
import './UserScreen.css';
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

function UserScreen({ onBack }) {
  const [showPopup, setShowPopup] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);


  /**
   * Opens the visualization popup.
   */
  const handleVisualizeClick = () => {
    console.log("Visualize clicked!");
    setShowPopup(true);
  };

  /**
   * Closes the visualization popup.
   */
  const handleClosePopup = () => {
    setShowPopup(false);
  };

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  async function uploadFile(file) {
    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);

      console.log("uploading file: " + formData)
      const response = await fetch('/api/files', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        console.error('Error uploading file:', response);
        throw new Error('Upload failed');
      }

      // Get the modified file from the response
      const modifiedFile = await response.blob();

      // Create a download link for the modified file
      const downloadUrl = window.URL.createObjectURL(modifiedFile);
      const fileName = response.headers.get('X-Modified-Filename') || 'modified_file.txt';

      // Create a temporary link and trigger download
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);

    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Failed to upload file. Please try again.');
    } finally {
      setUploading(false);
    }
  }

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = e.dataTransfer.files;
    if(files.length > 1) alert(
      "You can only upload one file at a time. Please try again."
    ) // Limit to one file for now
    if (files && files[0]) {
      // Handle the file upload here
      console.log("File dropped:", files[0]);
      uploadFile(files[0]);
    }
  }, []);

  const handleFileInput = (e) => {
    const files = e.target.files;
    if (files && files[0]) {
      // Handle the file upload here
      console.log("File selected:", files[0]);
      uploadFile(files[0]);
    }
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
          <div
            className={`upload-area ${dragActive ? 'drag-active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              id="file-input"
              onChange={handleFileInput}
              style={{ display: 'none' }}
            />
            <label htmlFor="file-input" className="upload-label">
              <div className="upload-content">
                {uploading ? (
                  <p>Uploading...</p>
                ) : (
                  <>
                    <p>Drag and drop files here</p>
                    <p>or</p>
                    <button className="upload-button" onClick={() => document.getElementById('file-input').click()}>
                      Choose File
                    </button>
                  </>
                )}
              </div>
            </label>
          </div>


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
