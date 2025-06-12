import React, { useCallback, useContext, useEffect, useState } from 'react';
import Select from 'react-select';
import './globalstyle.css';
import FileTableEntry from './components/FileTableEntry.jsx';
import { LanguageContext } from './main.jsx';
import { constructDownloadURL, handleDownload, handleFileUpload, handlePDFExport, handleSVGExport, handleVisualize } from './FileAPI.js';

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
  const [departments, setDepartments] = useState([]);
  const [selectedDepartment, setSelectedDepartment] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  const t = useContext(LanguageContext);

  useEffect(() => {
    fetchDepartments();
  }, []);

  const fetchDepartments = async () => {
    try {
      const response = await fetch('/api/admin/departments');
      if (response.ok) {
        const data = await response.json();
        setDepartments(data.departments);

        // Auto-select if only one department
        if (data.departments.length === 1) {
          setSelectedDepartment({
            value: data.departments[0].id,
            label: data.departments[0].name,
          });
        }
      }
    }
    catch (error) {
      console.error('Error fetching departments:', error);
      setErrorMessage('Failed to load departments');
    }
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
   * Handles file upload to the server.
   *
   * @param file {Object} - The file to be uploaded.
   * @returns {Promise<void>} - A promise that resolves when the file is uploaded.
   */
  async function handleFileUploadAction(file) {
    // Clear any previous error
    setErrorMessage('');

    // Check if department is selected
    if (!selectedDepartment) {
      setErrorMessage(t.departmentRequired || 'Please select a department before uploading');
      return;
    }

    // Make sure that the file is a JSON file
    if (!file.name.toLowerCase().endsWith('.json')) {
      setErrorMessage(t.invalidFileType || 'Please upload a JSON file');
      return;
    }

    setUploading(true);
    try {
      const data = await handleFileUpload(file, selectedDepartment.value);
      if (data === null) return;

      const departmentName = departments.find(d => d.id === selectedDepartment.value)?.name || 'Unknown';

      setFiles(prevFiles => [{
        id: data.id,
        filename: data.filename,
        department: departmentName,
        time: new Date().toISOString(),
      }, ...prevFiles]);

      // Clear any error message on successful upload
      setErrorMessage('');
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
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (uploading) return;

    const files = e.dataTransfer.files;
    if (files.length > 1) {
      setErrorMessage(t.uploadLimitExceeded || 'You can only upload one file at a time. Please try again.');
      return;
    }
    if (files && files[0]) {
      handleFileUploadAction(files[0]);
    }
  }, [uploading, selectedDepartment]);

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

  const departmentOptions = departments.map(dept => ({
    value: dept.id,
    label: dept.name,
  }));

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

          {/* Department Selector */}
          <div className="department-selector-section">
            <label className="department-label">
              <p>{t.selectDepartment || 'Select Department'}</p>
              <Select
                value={selectedDepartment}
                onChange={(value) => {
                  setSelectedDepartment(value);
                  setErrorMessage(''); // Clear error when department is selected
                }}
                options={departmentOptions}
                placeholder={t.selectDepartmentPlaceholder || 'Select a department...'}
                className="department-select"
                classNamePrefix="react-select"
                isDisabled={departments.length === 1}
              />
            </label>
          </div>

          {/* Error Message Display */}
          {errorMessage && (
            <div className="error-message">
              {errorMessage}
            </div>
          )}

          {/* Drop zone area with drag and drop event handlers */}
          <div
            className={`upload-area ${dragActive ? 'drag-active' : ''} ${!selectedDepartment ? 'upload-disabled' : ''}`}
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
                    disabled={!selectedDepartment}
                  />
                  <button
                    className="btn-blue"
                    onClick={() => {
                      if (!selectedDepartment) {
                        setErrorMessage(t.selectDepartmentFirst || 'Please select a department first');
                      }
                      else {
                        document.getElementById('file-input').click();
                      }
                    }}
                    disabled={!selectedDepartment}
                  >
                    {t.chooseFile}
                  </button>
                  {!selectedDepartment && (
                    <p className="upload-hint">{t.selectDepartmentFirst || 'Please select a department above'}</p>
                  )}
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
                    () => {
                      const url = constructDownloadURL([file.id]);
                      if (url !== null) handleVisualize(url);
                    }
                  }
                  onDownload={
                    () => {
                      const url = constructDownloadURL([file.id]);
                      if (url !== null) handleDownload(url, file.filename);
                    }
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
                  () => {
                    const url = constructDownloadURL([currentFile.id]);
                    if (url !== null) handleSVGExport(url, currentFile.id);
                  }
                }
              >
                SVG
              </button>
              <button
                className="popup-button"
                onClick={
                  () => {
                    const url = constructDownloadURL([currentFile.id]);
                    if (url !== null) handlePDFExport([url], [currentFile.id]);
                  }
                }
              >
                PDF
              </button>
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
