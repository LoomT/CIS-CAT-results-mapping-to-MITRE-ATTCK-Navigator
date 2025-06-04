import React, { useCallback, useContext, useState } from 'react';
import './globalstyle.css';
import FileTableEntry from './components/FileTableEntry.jsx';
import { LanguageContext } from './main.jsx';
import { constructDownloadURL, handleDownload, handleFileUpload, handleSVGExport, handleVisualize } from './FileAPI.js';

/**
 * UserScreen Component
 * ---------------------
 * Provides the main interface for regular users. Includes:
 * - File upload section
 * - A list of files with actions for visualization and download.
 * - A popup for choosing visualization formats (SVG or PNG).
 */

function UserScreen() {
  const [showPopup, setShowPopup] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [files, setFiles] = useState([]);
  const [currentFile, setFile] = useState({});
  const t = useContext(LanguageContext);

  /**
   * Opens the export popup.
   */
  const handleExportClick = (file) => {
    setFile(file);
    setShowPopup(true);
  };

  /**
   * Closes the visualization popup.
   */
  const handleClosePopup = () => {
    setShowPopup(false);
  };

  /**
   * Handles drag events. Sets the dragActive state to true when dragging over the drop zone
   * and false when leaving.
   *
   * @type {(function(*): void)|*} - The event handler function.
   * @param e {object} - The drag event.
   */
  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    }
    else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  /**
   * Handles file upload to the server.
   *
   * @param file {Object} - The file to be uploaded.
   * @returns {Promise<void>} - A promise that resolves when the file is uploaded.
   */
  async function handleFileUploadAction(file) {
    // Make sure that the file is a JSON file
    if (!file.name.toLowerCase().endsWith('.json')) {
      alert('Please upload a JSON file');
      return;
    }

    setUploading(true);
    handleFileUpload(file)
      .then((data) => {
        if (!data) return;
        // Append the new file to the files state
        setFiles(prevFiles => [{
          id: data.id,
          filename: data.filename,
          department: 'Default Department', // might want to make this dynamic
          time: new Date().toISOString(),
        }, ...prevFiles]);
      })
      .then(() => setUploading(false));
  }

  /**
   * Handles file drop event.
   *
   * @type {(function(*): void)|*} - The event handler function.
   * @param e {object} - The drop event, contains the files.
   */
  const handleDrop = useCallback((e) => {
    e.preventDefault(); // Prevent default browser behavior (e.g., open file in new tab)
    e.stopPropagation(); // Prevent event bubbling up to parent elements
    setDragActive(false);
    if (uploading) return; // Don't allow dropping a file if already uploading
    console.log('Drop event:', e);
    const files = e.dataTransfer.files;
    if (files.length > 1) alert(
      'You can only upload one file at a time. Please try again.',
    ); // Limit to one file for now
    if (files && files[0]) {
      // Handle the file upload here
      console.log('File dropped:', files[0]);
      handleFileUploadAction(files[0]);
    }
  }, [uploading]);

  /**
   * Handles file upload from the file input element triggered by the button.
   *
   * @param e {object} - The input change event, contains the files.
   */
  const handleFileInput = (e) => {
    const files = e.target.files;
    if (files && files[0]) {
      // Handle the file upload here
      console.log('File selected:', files[0]);
      handleFileUploadAction(files[0]);
    }
  };

  return (
    <div className="full-panel" data-testid="user-screen">
      {/* Top Center Title */}
      <div className="user-title" data-testid="user-screen-page-title">
        {t.userOverview}
      </div>

      {/* Side-by-side Content Area */}
      <div className="content-area">
        {/* Upload Section */}
        <div className="card upload-section" data-testid="user-screen-upload-section">
          <div className="section-header">
            <h2>{t.uploadFile}</h2>
            <p>{t.dragAndDrop}</p>
          </div>

          {/* Drop zone area with drag and drop event handlers */}
          <div
            className={`upload-area ${dragActive ? 'drag-active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="upload-content">
              {/* eslint-disable-next-line @stylistic/multiline-ternary */}
              {uploading ? (
                <p>{t.uploading}</p>
              ) : (
                <>
                  <p>{t.dragAndDropShort}</p>
                  <p>{t.orr}</p>
                  <input
                    type="file"
                    id="file-input"
                    onChange={handleFileInput}
                    accept=".json"
                    style={{ display: 'none' }}
                  />
                  <button
                    className="btn-blue"
                    onClick={() => document.getElementById('file-input').click()}
                  >
                    {t.chooseFile}
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* File Table Section */}
        <div className="card file-table-section" data-testid="user-screen-file-table-section">
          <div className="section-header">
            <h2>{t.filesList}</h2>
            <p>{t.fileTableDesc}</p>
          </div>
          <table>
            <thead>
              <tr>
                <th>{t.name}</th>
                <th>{t.department}</th>
                <th>{t.date}</th>
                <th>{t.actions}</th>
              </tr>
            </thead>
            { /* Maps each file to be displayed with its name, department, time, and actions (visualise and download) */}
            <tbody>
              {files.map(file => (
                <FileTableEntry
                  key={file.id}
                  fileId={file.id}
                  filename={file.filename}
                  department={file.department}
                  time={file.time}
                  onExport={
                    () => handleExportClick(file)
                  }
                  onVisualize={
                    () => constructDownloadURL([file.id])
                      .then(
                        uri => handleVisualize(uri),
                        (_) => {}, // Ignore errors
                      )
                  }
                  onDownload={
                    () => constructDownloadURL([file.id])
                      .then(
                        uri => handleDownload(uri, file.filename),
                        (_) => {}, // Ignore errors
                      )
                  }
                  showCheckbox={false}
                />
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Visualization Selection Popup */}
      {showPopup && (
        <div className="popup-overlay">
          <div className="popup">
            <h3 className="popup-heading">{t.chooseFormat}</h3>
            <div className="popup-buttons">
              <button
                className="popup-button"
                onClick={
                  () => constructDownloadURL([currentFile.id])
                    .then(
                      uri => handleSVGExport(uri, currentFile.id),
                      (_) => {}, // Ignore errors
                    )
                }
              >
                SVG
              </button>
              <button className="popup-button">PNG</button>
              <button className="popup-cancel" onClick={handleClosePopup}>
                {t.cancel}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserScreen;
