import React, { useContext, useEffect, useState } from 'react';
import './globalstyle.css';
import './popups.css';
import FileTableEntry from './components/FileTableEntry.jsx';
import NavigatorAPI from './NavigatorAPI.js';
import { LanguageContext } from './main.jsx';

/**
 * AdminOverview Component
 * ---------------------
 * Provides the main interface for admins. Includes:
 * - A search section with (currently nonfunctional) toggle for the departments and a search bar
 * - A list of files with actions for visualization and download, and a checkbox to select multiple rows (currently not functional)
 * - A popup for choosing visualization formats (SVG or PNG).
 */

function AdminOverview() {
  const [showExportPopup, setShowExportPopup] = useState(false);
  const [exportFile, setExportFile] = useState({});
  const [exportAggregate, setExportAggregate] = useState(false);
  const [hostSearch, setHostSearch] = useState(''); // TODO: currently unused
  const [files, setFiles] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const t = useContext(LanguageContext);

  useEffect(() => {
    // Call the handleRefresh function when the component mounts
    handleRefresh();
  }, []);

  /**
   * Opens the visualization popup.
   */
  const handleVisualizeClick = (file, aggregate) => {
    let uri = new URL(location.href);

    if (aggregate) {
      if (selectedFiles.length === 0) {
        alert('No files selected!');
        return;
      }
      selectedFiles.forEach(id => uri.searchParams.append('id', id));
      uri.pathname = `/api/files/aggregate`;
    }
    else {
      uri.pathname = `/api/files/${file.id}`;
    }
    let targetWindow = window.open('/attack-navigator/index.html');

    let client = new NavigatorAPI(targetWindow, uri.toString(), false);
  };

  /**
   * Opens the export popup.
   */
  const handleExportClick = (file, aggregate) => {
    setExportFile(file);
    setExportAggregate(aggregate);
    setShowExportPopup(true);
  };

  /**
   * Closes the export popup.
   */
  const handlePopupClose = () => {
    setShowExportPopup(false);
  };

  const handleDownload = async (fileId, fileName) => {
    console.log('downloading file: ' + fileId);
    let response;
    try {
      response = await fetch(`/api/files/${fileId}`);
    }
    catch (error) {
      console.error('Error downloading file:', error);
      if (error.name === 'AbortError') {
        alert('Downloading was cancelled. Please try again.');
      }
      else if (error instanceof TypeError) {
        alert('Network error occurred. Please check your internet connection and try again.');
      }
      else {
        // Fallback for unknown errors
        alert('Failed to download file. Please try again.');
      }
      return;
    }

    if (!response.ok) {
      console.error('Error downloading file:', response);
      switch (response.status) {
        case 400:
          alert('Invalid file id');
          break;
        case 404:
          alert('File not found');
          break;
        case 500:
          alert('Server error occurred while downloading the file. Please try again later.');
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
    }
    catch (error) {
      if (error instanceof DOMException) {
        console.log('Download was cancelled by the user.');
      }
      else {
        // Fallback for unknown errors
        console.error('Error accessing or decoding response body:', error);
        alert('Error accessing or decoding response body. Please try again.');
      }
      return;
    }

    // Create a download link for the modified file
    const downloadUrl = window.URL.createObjectURL(file);

    // Create a temporary link and trigger download
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(downloadUrl);
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
    newIframe.id = exportFile.id; // TODO @Qyn what IFrame to use when aggregating?

    let frame = document.getElementById(exportFile.id);
    frame.parentNode.replaceChild(newIframe, frame);

    if (exportAggregate) {
      if (selectedFiles.length === 0) {
        alert('No files selected!');
        return;
      }
      selectedFiles.forEach(id => uri.searchParams.append('id', id));
      uri.pathname = `/api/files/aggregate`;
    }
    else {
      uri.pathname = `/api/files/${exportFile.id}`;
    }
    let targetWindow = newIframe.contentWindow;

    let client = new NavigatorAPI(targetWindow, uri.toString(), true);
  };

  /**
   * Asynchronous function to refresh files by fetching data from the designated API endpoint.
   * Handles various error scenarios such as network issues, server errors, and user-initiated cancellations.
   * The function processes the response, maps the data, and updates the list of files in the application state.
   *
   * Key error handling:
   * - Displays alerts for network issues, aborted requests, server errors, and decoding problems.
   * - Logs detailed error information to the console for debugging purposes.
   *
   * Behavior:
   * - Makes an HTTP GET request to fetch files metadata from the `/api/files` endpoint.
   * - Maps the response data to a standardized format before updating the state.
   */
  const handleRefresh = async () => {
    let response;
    try {
      response = await fetch('/api/files/');
    }
    catch (error) {
      console.error('Error refreshing files:', error);
      if (error.name === 'AbortError') {
        alert('Refresh was cancelled. Please try again.');
      }
      else if (error instanceof TypeError) {
        alert('Network error occurred. Please check your internet connection and try again.');
      }
      else {
        // Fallback for unknown errors
        alert('Failed to refresh files. Please try again.');
      }
      return;
    }
    if (!response.ok) {
      // Only 500 is possible for this endpoint at the moment
      console.error('Error fetching files:', response);
      alert('Server error occurred while refreshing the files. Please try again later.');
      return;
    }
    let files;
    try {
      files = (await response.json()).files;
    }
    catch (error) {
      console.error('Error downloading file:', error);
      if (error instanceof DOMException) {
        console.log('Refresh was cancelled by the user.');
      }
      else {
        // Fallback for unknown errors
        console.error('Error accessing or decoding response body:', error);
        alert('Error accessing or decoding response body. Please try again.');
      }
      return;
    }

    console.log(files);

    setFiles(files.map(file => ({
      id: file.id,
      filename: file.filename,
      department: 'Default Department',
      time: new Date().toISOString(),
    })));
  };

  /**
   * Handles the change event for a checkbox by toggling its checked state
   * and updating the selected files list accordingly.
   *
   * @param {boolean} isChecked - The current checked state of the checkbox.
   * @param {string|number} fileId - The unique identifier of the file associated with the checkbox.
   */
  const handleCheckboxChange = (isChecked, fileId) => {
    isChecked = !isChecked;
    setSelectedFiles((prevSelected) => {
      // If the ID is already in the array, remove it; otherwise, add it
      if (!isChecked) {
        return prevSelected.filter(id => id !== fileId);
      }
      else {
        return [...prevSelected, fileId];
      }
    });
  };

  /**
   * Handles the download of selected files by aggregating them into a single file.
   *
   * This function checks if any files are selected, and if so, constructs a request
   * to download the aggregated file. The aggregated file is then automatically downloaded.
   * If no files are selected or an error occurs during the process,
   * appropriate messages are logged and/or alerted to the user.
   *
   * Error Handling:
   * - Alerts the user if no files are selected.
   * - Handles HTTP response errors (e.g., 400, 404, 500) and displays an appropriate message.
   * - Catches network errors or cancellation of the download.
   *
   * Filename:
   * - The function attempts to retrieve the filename from the `Content-Disposition` header.
   * - If no filename is provided in the header, a default filename (`combined_results.json`) is used.
   *
   * Additional Notes:
   * - The combined file is fetched from the `/api/files` endpoint with query parameters specifying
   *   the selected file IDs and an aggregate flag.
   * - A temporary hyperlink element is created to trigger the download and is removed afterward.
   *
   * Preconditions:
   * - `selectedFiles` is an array containing the IDs of the files to be downloaded. It should be declared
   *   and populated elsewhere in the scope.
   */
  const handleDownloadOnSelectedFiles = async () => {
    if (selectedFiles.length === 0) {
      alert('No files selected!');
      return;
    }

    console.log('Downloading aggregated selected files:', selectedFiles);
    try {
      // Build the URL with all file IDs as query parameters
      const queryParams = new URLSearchParams();
      selectedFiles.forEach(id => queryParams.append('id', id));
      const url = `/api/files/aggregate?${queryParams.toString()}`;

      // Fetch the combined file
      const response = await fetch(url);

      if (!response.ok) {
        console.error('Error downloading combined files:', response);

        let errorMessage;
        switch (response.status) {
          case 400:
            errorMessage = 'Invalid file ids';
            break;
          case 404:
            errorMessage = 'One or more files not found';
            break;
          case 500:
            errorMessage = 'Server error occurred while combining files';
            break;
          default:
            errorMessage = `Download failed: ${response.statusText}`;
        }

        alert(errorMessage);
        return;
      }

      // Get the combined file blob
      const file = await response.blob();

      // Create a download link and trigger download
      const downloadUrl = window.URL.createObjectURL(file);
      const a = document.createElement('a');
      a.href = downloadUrl;

      // Get filename from Content-Disposition header if available
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'combined_results.json';

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1];
        }
      }

      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);

      console.log('Combined files downloaded successfully');
    }
    catch (error) {
      console.error('Error downloading combined files:', error);

      let errorMessage = 'Failed to download combined files';
      if (error.name === 'AbortError') {
        errorMessage = 'Download was cancelled';
      }
      else if (error instanceof TypeError) {
        errorMessage = 'Network error occurred. Please check your internet connection and try again.';
      }
      else if (error instanceof DOMException) {
        console.log('Download was cancelled by the user.');
      }
      else {
        // Fallback for unknown errors
        console.error('Error accessing or decoding response body:', error);
        alert('Error accessing or decoding response body. Please try again.');
      }
      alert(errorMessage);
    }
  };

  return (
    <div className="full-panel">
      {/* Top Title */}
      <div className="user-title">{t.adminOverview}</div>

      {/* Section with selectors (department toggle and search bar) */}
      <div className="content-area">
        <div className="card admin-side-section">
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
              onChange={e => setHostSearch(e.target.value)}
            />
          </div>
          <button className="btn-blue" onClick={() => handleRefresh()}>Refresh</button>
          <div>
            <h2>Aggregation</h2>
            {selectedFiles.length === 0
              ? (
                  <>
                    <p>No files selected</p>
                    <div className="button-container">
                      <button className="btn-purple" disabled={true}>Export</button>
                      <button className="btn-blue" disabled={true}>Visualize</button>
                      <button className="btn-green" disabled={true}>Download</button>
                    </div>
                  </>
                )
              : (
                  <>
                    <p>{'Selected files: ' + selectedFiles.length}</p>
                    <div className="button-container">
                      <button className="btn-purple" onClick={() => handleExportClick(null, true)}>Export</button>
                      <button className="btn-blue" onClick={() => handleVisualizeClick(null, true)}>Visualize</button>
                      <button className="btn-green" onClick={() => handleDownloadOnSelectedFiles()}>Download</button>
                    </div>
                  </>
                )}
          </div>
        </div>

        {/* File Table Section */}
        <div className="card file-table-section">
          <h2>{t.filesList}</h2>
          {/* TODO */}
          <p className="section-description">Description placeholder</p>
          <table>
            <thead>
              <tr>
                {/* TODO */}
                <th>Select</th>
                <th>{t.name}</th>
                <th>{t.department}</th>
                <th>{t.date}</th>
                <th>{t.actions}</th>
              </tr>
            </thead>
            <tbody>
              {/* Map files to table rows */}
              {files.map(file => (
                <FileTableEntry
                  key={file.id}
                  id={file.id}
                  filename={file.filename}
                  department={file.department}
                  time={file.time}
                  onExport={() => handleExportClick(file, false)}
                  onVisualize={() => handleVisualizeClick(file, false)}
                  onDownload={() => handleDownload(file.id, file.filename)}
                  showCheckbox={true}
                  onCheckboxChange={handleCheckboxChange}
                />
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Visualisation popup */}
      {showExportPopup && (
        <div className="popup-overlay">
          <div className="popup">
            <h3 className="popup-heading">{t.chooseFormat}</h3>
            <div className="popup-buttons">
              <button className="popup-button" onClick={handleSVGExportClick}>SVG</button>
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
