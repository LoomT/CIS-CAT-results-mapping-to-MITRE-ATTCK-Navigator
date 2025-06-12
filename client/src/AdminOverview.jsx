import React, { useContext, useEffect, useState } from 'react';
import Select from 'react-select';
import './globalstyle.css';
import FileTableEntry from './components/FileTableEntry.jsx';
import { LanguageContext } from './main.jsx';
import {
  constructDownloadURL,
  fetchFilesMetadata,
  handleDownload,
  handlePDFExport,
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
  const [files, setFiles] = useState([]);
  const [exportFile, setExportFile] = useState({});
  const [exportAggregate, setExportAggregate] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const t = useContext(LanguageContext);

  useEffect(() => {
    // Call the handleRefresh function when the component mounts
    handleRefresh();
  }, []);
  /**
   * Defines options for the department dropdown. Probably a TODO to not hardcode this
   */
  const optionsDepts = [
    { value: 'dept1', label: 'Department 1' },
    { value: 'dept2', label: 'Department 2' },
  ];
  /**
   * Defines options for the benchmark type dropdown. Probably a TODO to not hardcode this
   */
  const optionsBMs = [
    { value: 'enterprise', label: 'Enterprise' },
    { value: 'mobile', label: 'Mobile' },
  ];
  /**
 * Defines options for the benchmark type dropdown. Probably a TODO to not hardcode this
 */
  const optionsHosts = [
    { value: 'ho1', label: 'Host 1' },
    { value: 'ho2', label: 'Host 2' },
  ];
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
    fetchFilesMetadata().then((result) => {
      setFiles(result.data.map(file => ({
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
          <h2>{t.filterFiles}</h2>
          <div className="section-header">
            <p>{t.searchFiles}</p>
            <input type="text" placeholder="Search files..." />
          </div>

          <div className="section-header">
            <p>{t.departmentFilter}</p>
            <Select
              isMulti
              options={optionsDepts}
              className="department-filter-testid"
              classNamePrefix="react-select"
            />
          </div>

          <div className="section-header">
            <label>
              <p>{t.onlyLatestFiles}</p>
              <input type="checkbox" />
            </label>
          </div>

          <div className="section-header">
            <p>{t.searchHosts}</p>
            <Select
              isMulti
              options={optionsHosts}
              className="hostname-filter-testid"
              classNamePrefix="react-select"
            />
          </div>

          <div className="section-header">
            <p>{t.dateRange}</p>
            <p>From</p>
            <input type="datetime-local" />
            <p>To</p>
            <input type="datetime-local" />
          </div>

          <div className="section-header">
            <p>{t.benchmarkTypes}</p>
            <Select
              isMulti
              options={optionsBMs}
              className="benchmark-filter-testid"
              classNamePrefix="react-select"
            />
          </div>
          <button className="btn-blue" onClick={() => handleRefresh()}>Refresh</button>
          <div>
            <h2>Aggregation</h2>
            <iframe id="aggregateFrame"></iframe>
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
                          () => {
                            const url = constructDownloadURL(selectedFiles);
                            if (url !== null) handleVisualize(url);
                          }
                        }
                      >
                        Visualize
                      </button>
                      <button
                        className="btn-green"
                        onClick={
                          () => {
                            const url = constructDownloadURL(selectedFiles);
                            if (url !== null) handleDownload(url, 'combined_results.json');
                          }
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
          <table className="files-table">
            <thead>
              <tr>
                <th>{t.select}</th>
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
                  fileId={file.id}
                  filename={file.filename}
                  department={file.department}
                  time={file.time}
                  onExport={
                    () => handleExportClick(file, false)
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
                    ? () => {
                        const url = constructDownloadURL(selectedFiles);
                        if (url !== null) handleSVGExport(url, 'aggregateFrame');
                      }
                    : () => {
                        const url = constructDownloadURL([exportFile.id]);
                        if (url !== null) handleSVGExport(url, exportFile.id);
                      }
                }
              >
                SVG
              </button>

              {exportAggregate
                ? (
                    <>
                      <button
                        className="popup-button"
                        onClick={() => {
                          const url = constructDownloadURL(selectedFiles);
                          if (url !== null) handlePDFExport([url], ['aggregateFrame']);
                        }}
                      >
                        Aggregate PDF
                      </button>
                      <button
                        className="popup-button"
                        onClick={() => {
                          const uris = selectedFiles.map(fileId => constructDownloadURL([fileId]));
                          if (uris.every(url => url !== null)) handlePDFExport(uris, selectedFiles);
                        }}
                      >
                        All PDF
                      </button>
                    </>
                  )
                : (
                    <button
                      className="popup-button"
                      onClick={() => {
                        const url = constructDownloadURL([exportFile.id]);
                        if (url !== null) handlePDFExport([url], [exportFile.id]);
                      }}
                    >
                      PDF
                    </button>
                  )}

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
