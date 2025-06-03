import React, { useContext, useEffect, useState } from 'react';
import './globalstyle.css';
import './popups.css';
import FileTableEntry from './components/FileTableEntry.jsx';
import { LanguageContext } from './main.jsx';
import {
  constructDownloadURL,
  fetchFilesMetadata,
  handleDownload,
  handleSVGExport,
  handleVisualize,
} from './FileAPI.js';

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

  const handleRefresh = () => {
    fetchFilesMetadata().then((files) => {
      setFiles(files.map(file => ({
        id: file.id,
        filename: file.filename,
        department: 'Default Department',
        time: new Date().toISOString(),
      })));
    });
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
                      <button
                        className="btn-purple"
                        onClick={
                          () => handleExportClick(null, true)
                        }
                      >
                        Export
                      </button>
                      <button
                        className="btn-blue"
                        onClick={
                          () => constructDownloadURL(selectedFiles)
                            .then(
                              uri => handleVisualize(uri),
                              (_) => {}, // Ignore errors
                            )
                        }
                      >
                        Visualize
                      </button>
                      <button
                        className="btn-green"
                        onClick={
                          () => constructDownloadURL(selectedFiles)
                            .then(
                              uri => handleDownload(uri, 'combined_results.json'),
                              (_) => {}, // Ignore errors
                            )
                        }
                      >
                        Download
                      </button>
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
                  onExport={
                    () => handleExportClick(file, false)
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
              <button
                className="popup-button"
                onClick={
                  exportAggregate
                    ? () => constructDownloadURL(selectedFiles)
                        .then(
                          uri => handleSVGExport(uri, null), // TODO
                          (_) => {}, // Ignore errors
                        )
                    : () => constructDownloadURL([exportFile.id])
                        .then(
                          uri => handleSVGExport(uri, exportFile.id),
                          (_) => {}, // Ignore errors
                        )
                }
              >
                SVG
              </button>
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
