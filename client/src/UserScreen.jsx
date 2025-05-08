import React, {useCallback, useState} from "react";
import "./UserScreen.css";
import "./popups.css";
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
 * @param {function} onBack - Callback to navigate back to the previous screen (typically home).
 * @return {React.JSX.Element} - The rendered UserScreen component.
 */

function UserScreen({ onBack }) {
  const [showPopup, setShowPopup] = useState(false);
  const [dragActive, setDragActive] = useState(false);
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
      alert("Please upload a JSON file only");
      return;
    }

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append("file", file);

      console.log("uploading file: " + formData)
      const response = await fetch("/api/files", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        console.error("Error uploading file:", response);
        alert("Failed to upload file. Please try again.");
        return
      }

      const data = await response.json();
      console.log("File uploaded successfully. File ID:", data.id);

      // Append the new file to the files state
      setFiles(prevFiles => [{
        id: data.id,
        filename: data.filename,
        department: "Default Department", // might want to make this dynamic
        time: new Date().toISOString()
      }, ...prevFiles]);

    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Failed to upload file. Please try again.");
    } finally {
      setUploading(false);
    }
  }

  const handleDownload = async (fileId, fileName) => {
    try {
      console.log("downloading file: " + fileId)
      const response = await fetch(`/api/files/${fileId}`);

      if (!response.ok) {
        console.error("Error downloading file:", response);
        alert("Failed to download file. Please try again.");
        return
      }

      // Get the converted file from the response
      const file = await response.blob();

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
    } catch (error) {
      console.error("Error downloading file:", error);
      alert("Failed to download file. Please try again.");
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
    <div className="user-screen">

      {/* Top Navigation Bar */}
      <div className="top-bar">
        <div className="back-text" onClick={onBack}>← Back</div>
        <div className="title-text">User Overview</div>
      </div>

      {/* Side-by-side Content Area container */}
      <div className="content-area">
        {/* Left section for file upload functionality */}
        <div className="upload-section">
          <h2>Upload a File</h2>
          {/* Drop zone area with drag and drop event handlers */}
          <div
            className={`upload-area ${dragActive ? "drag-active" : ""}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {/* Upload status and instructions */}
            <div className="upload-content">
              {uploading ? (
                <p>Uploading...</p>
              ) : (
                <>
                  {/* Instructions shown when not uploading */}
                  <p>Drag and drop files here</p>
                  <p>or</p>
                  {/* Hidden file input element triggered by button */}
                  <input
                    type="file"
                    id="file-input"
                    onChange={handleFileInput}
                    accept=".json"
                    style={{display: "none"}}
                  />
                  <button className="upload-button" onClick={
                    () => document.getElementById("file-input").click()
                  }>
                    Choose File
                  </button>
                </>
              )}
            </div>
          </div>


          {/* Run Benchmark Section */}
          <h2>Run Benchmark</h2>
          {/* Same styling as Upload File */}
          <button className="upload-button">Run Benchmark</button>
        </div>

        {/* File Table Section */}
        <div className="file-table-section">
          <h2>Files List</h2>
          <table className="file-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Department</th>
                <th>Time</th>
                <th>Actions</th>
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
                  onVisualize={() => handleVisualizeClick()}
                  onDownload={() => handleDownload(file.id, file.filename)}
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
