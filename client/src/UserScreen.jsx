import React, { useCallback, useContext, useState } from 'react';
import { Link } from 'react-router-dom';
import './globalstyle.css';
import backIcon from './assets/back.png';
import FileTableEntry from './components/FileTableEntry.jsx';
import NavigatorAPI from './NavigatorAPI.js';
import { LanguageContext } from './main.jsx';

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
   * Opens the visualization popup.
   */
  const handleVisualizeClick = (file) => {
    let uri = new URL(location.href);

    uri.pathname = `/api/files/${file.id}`;
    let targetWindow = window.open('/attack-navigator/index.html');

    let client = new NavigatorAPI(targetWindow, uri.toString(), false);
  };

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
   * Handles file upload to the server and downloads the modified file from the response.
   *
   * @param file {File} - The file to be uploaded.
   * @returns {Promise<void>} - A promise that resolves when the file is uploaded and downloaded.
   */
  async function uploadFile(file) {
    // Make sure that the file is a JSON file
    if (!file.name.toLowerCase().endsWith('.json')) {
      alert('Please upload a JSON file');
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      console.log('uploading file: ' + formData);
      let response;
      try {
        response = await fetch('/api/files/', {
          method: 'POST',
          body: formData,
        });
      }
      catch (error) {
        // TODO maybe try doing the fetch a few times before failing on some type of errors?
        if (error instanceof DOMException && error.name === 'AbortError') {
          console.log('Upload was cancelled by the user.');
        }
        else if (error instanceof TypeError) {
          console.error('Error uploading file:', error);
          alert('Network error occurred. Please check your internet connection and try again.');
        }
        else {
          // Fallback for unknown errors
          console.error('Error uploading file:', error);
          alert('Failed to upload file. Please try again.');
        }
        return;
      }

      if (!response.ok) {
        console.error('Error uploading file:', response);
        switch (response.status) {
          case 400:
            alert('Invalid file format or empty file. Please ensure you\'re uploading a valid JSON file.');
            break;
          case 500:
            alert('Server error occurred while processing the file. Please try again later.');
            break;
          default:
            alert(`Upload failed: ${response.statusText}. Please try again.`);
        }
        return;
      }
      let data;
      try {
        data = await response.json();
      }
      catch (error) {
        if (error instanceof DOMException) {
          console.log('Upload was cancelled by the user.');
        }
        else if (error instanceof SyntaxError) {
          console.error('Error parsing JSON:', error);
          alert('Response from server is not valid JSON. Please try again.');
        }
        else {
          // Fallback for unknown errors
          console.error('Error accessing or decoding response body:', error);
          alert('Error accessing or decoding response body. Please try again.');
        }
        return;
      }

      console.log('File uploaded successfully. File ID:', data.id);

      // Append the new file to the files state
      setFiles(prevFiles => [{
        id: data.id,
        filename: data.filename,
        department: 'Default Department', // might want to make this dynamic
        time: new Date().toISOString(),
      }, ...prevFiles]);
    }
    finally {
      setUploading(false);
    }
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
      uploadFile(files[0]);
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
      uploadFile(files[0]);
    }
  };

  /**
   * Handle SVG export & download
   */
  const handleSVGExportClick = () => {
    let uri = new URL(location.href);

    /**
     * Dirty workaround to get a fresh handle to the iframe window
     * There are a couple of issues with reusing the old one
     * Specifically that navigation takes time. A lot of time
     * So when we modify the src the window will still point to the
     * old window object. Theres definitely a better solution than this
     * But let's mark this as TODO */

    const newIframe = document.createElement('iframe');
    newIframe.sandbox = 'allow-scripts allow-same-origin allow-downloads';
    newIframe.src = '/attack-navigator/index.html';
    newIframe.id = currentFile.id;

    let frame = document.getElementById(currentFile.id);
    frame.parentNode.replaceChild(newIframe, frame);

    uri.pathname = `/api/files/${currentFile.id}`;
    let targetWindow = newIframe.contentWindow;

    let client = new NavigatorAPI(targetWindow, uri.toString(), true);
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
        <div className="card file-table-section full-panel" data-testid="user-screen-file-table-section">
          <div className="section-header">
            <h2>{t.filesList}</h2>
            <p>{t.fileTableDesc}</p>
          </div>
          <table className="files-table">
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
                  id={file.id}
                  filename={file.filename}
                  department={file.department}
                  time={file.time}
                  onExport={() => handleExportClick(file)}
                  onVisualize={() => handleVisualizeClick(file)}
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
              <button className="popup-button" onClick={handleSVGExportClick}>SVG</button>
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
