import React, {useCallback, useEffect, useState} from 'react';
import './globalstyle.css';
import './popups.css';
import backIcon from './assets/back.png';
import investigateIcon from './assets/investigate.png';
import "./FileTableEntry.jsx";
import FileTableEntry from "./FileTableEntry.jsx";

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
 * @param {function} onBack - Callback to navigate back to the previous screen (typically home).
 * @param t the translation mapping
 * @return {React.JSX.Element} - The rendered UserScreen component.
 */

function UserScreen({ onBack, t }) {
  const [showPopup, setShowPopup] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const [uploading, setUploading] = useState(false);
  const [files, setFiles] = useState([]);
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
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
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
    if (!file.name.toLowerCase().endsWith(".json")) {
      alert("Please upload a JSON file");
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      console.log("uploading file: " + formData)
      let response;
      try {
        response = await fetch("/api/files", {
          method: "POST",
          body: formData,
        });
      } catch (error) {
        // TODO maybe try doing the fetch a few times before failing on some type of errors?
        if (error instanceof DOMException && error.name === "AbortError") {
          console.log("Upload was cancelled by the user.")
        } else if (error instanceof TypeError) {
          console.error("Error uploading file:", error);
          alert("Network error occurred. Please check your internet connection and try again.");
        } else {
          // Fallback for unknown errors
          console.error("Error uploading file:", error);
          alert("Failed to upload file. Please try again.");
        }
        return;
      }

      if (!response.ok) {
        console.error("Error uploading file:", response);
        switch (response.status) {
        case 400:
          alert("Invalid file format or empty file. Please ensure you're uploading a valid JSON file.");
          break;
        case 500:
          alert("Server error occurred while processing the file. Please try again later.");
          break;
        default:
          alert(`Upload failed: ${response.statusText}. Please try again.`);
        }
        return;
      }
      let data;
      try {
        data = await response.json();
      } catch (error) {
        if (error instanceof DOMException) {
          console.log("Upload was cancelled by the user.")
        } else if (error instanceof SyntaxError) {
          console.error("Error parsing JSON:", error);
          alert("Response from server is not valid JSON. Please try again.");
        } else {
          // Fallback for unknown errors
          console.error("Error accessing or decoding response body:", error);
          alert("Error accessing or decoding response body. Please try again.");
        }
        return;
      }

      console.log("File uploaded successfully. File ID:", data.id);

      // Append the new file to the files state
      setFiles(prevFiles => [{
        id: data.id,
        filename: data.filename,
        department: "Default Department",
        size: "~10KB", // TODO: placeholder
        time: new Date().toISOString()
      }, ...prevFiles]);
    } finally {
      setUploading(false);
    }
  }

  useEffect(() => {
    if (uploadMessage) {
      const timer = setTimeout(() => setUploadMessage(''), 5000);
      return () => clearTimeout(timer);
    }
  }, [uploadMessage]);

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
    if (uploading) return // Don't allow dropping a file if already uploading
    console.log("Drop event:", e);
    const files = e.dataTransfer.files;
    if (files.length > 1) alert(
      "You can only upload one file at a time. Please try again."
    ) // Limit to one file for now
    if (files && files[0]) {
      // Handle the file upload here
      console.log("File dropped:", files[0]);
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
      console.log("File selected:", files[0]);
      uploadFile(files[0]);
    }
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
        <div className="card upload-section" data-testid="user-screen-upload-section">
          <div className="section-header">
            <h2>{t.uploadFile}</h2>
            <p>Drag and drop a file or click the area below to upload your JSON file.</p>
          </div>

          {/* Drop zone area with drag and drop event handlers */}
          <div
            className={`upload-area ${dragActive ? "drag-active" : ""}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept=".json"
              onChange={handleFileInput}
              style={{ display: 'none' }}
              id="file-upload-input"
            />
            <label htmlFor="file-upload-input" className="upload-label">
              Click here or drag a JSON file to upload
            </label>
          </div>

          {/* Run Benchmark Section */}
          <div className="section-header" style={{ marginTop: '2rem' }}>
            <h2>{t.runBenchmark}</h2>
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
          <table className="file-table">
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
              {/* Map files to table rows*/}
              {files.map((file) => (
                <FileTableEntry
                  key={file.id}
                  filename={file.filename}
                  size={file.size}
                  department={file.department}
                  time={file.time}
                  onVisualize={() => handleVisualizeClick()}
                  onDownload={() => handleDownload(file.id, file.filename)}
                  t={{visualize: "visualize", download:"download"}}
                />
              ))}
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
