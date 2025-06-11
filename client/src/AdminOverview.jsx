import React, { useContext, useEffect, useState } from 'react';
import Select from 'react-select';
import './globalstyle.css';
import FileTableEntry from './components/FileTableEntry.jsx';
import { LanguageContext } from './main.jsx';
import {
  constructDownloadURL,
  constructDownloadURLFromFileIds,
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
  const [files, setFiles] = useState([]);
  const [exportFile, setExportFile] = useState({});
  const [exportAggregate, setExportAggregate] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [optionsDepts, setOptionsDepts] = useState([]);
  const [selectedDepts, setSelectedDepts] = useState([]);
  const [optionsBenchTypes, setOptionsBenchTypes] = useState([]);
  const [selectedBenchTypes, setSelectedBenchTypes] = useState([]);
  const [optionsHosts, setOptionsHosts] = useState([]);
  const [selectedHosts, setSelectedHosts] = useState([]);
  const [searchText, setSearchText] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [totalNumberOfFiles, setTotalNumberOfFiles] = useState(0);
  const t = useContext(LanguageContext);

  useEffect(() => {
    // Load the options for the dropdowns when the component mounts
    fetchFilesMetadata().then((result) => {
      if (result === null) return;
      setOptionsDepts(result.filters.department.map(
        dept => ({ value: dept.id, label: dept.name }),
      ));
      setOptionsBenchTypes(result.filters.benchmark.map(
        bench => ({ value: bench.id, label: bench.name }),
      ));
      setOptionsHosts(result.filters.hostname.map(
        host => ({ value: host.id, label: host.name }),
      ));
      // Load the files on the file list
      handleRefresh(result);
    });
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

  /**
   * Asynchronous function to handle the refresh operation for file metadata.
   *
   * This function fetches metadata for files if a result parameter is not provided
   * or processes a provided result object. It updates the state with selected
   * properties of the file metadata.
   *
   * @async
   * @function
   * @param {Object|null} [result=null] - Optional result data containing metadata of files.
   * If no result is provided, the function will fetch data using `fetchFilesMetadata`.
   * @returns {void}
   */
  const handleRefresh = async (result = null) => {
    isLoading.current = true;
    setCurrentPage(0);

    if (result === null) {
      result = await fetchFilesMetadata(
        searchText,
        selectedDepts.map(dept => dept.value),
        selectedBenchTypes.map(bench => bench.value),
        selectedHosts.map(host => host.value),
        dateFrom,
        dateTo,
        0,
        pageSize,
      );
    }
    if (result === null) {
      isLoading.current = false;
      return;
    }

    setFiles(result.data.map(file => ({
      id: file.id,
      filename: file.filename,
      department: file.department ? file.department.name : 'None',
      time: file.time_created ? file.time_created.replace('T', ' ') : null,
    })));
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
            <input
              type="text"
              placeholder="Search files..."
              value={searchText}
              onChange={e => setSearchText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleRefresh();
                }
              }}
            />
          </div>

          <div className="section-header">
            <p>{t.departmentFilter}</p>
            <Select
              isMulti
              options={optionsDepts}
              value={selectedDepts}
              onChange={setSelectedDepts}
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
              value={selectedHosts}
              onChange={setSelectedHosts}
              className="hostname-filter-testid"
              classNamePrefix="react-select"
            />
          </div>

          <div className="section-header">
            <p>{t.dateRange}</p>
            <p>From</p>
            <input
              type="datetime-local"
              value={dateFrom}
              onChange={e => setDateFrom(e.target.value)}
            />
            <p>To</p>
            <input
              type="datetime-local"
              value={dateTo}
              onChange={e => setDateTo(e.target.value)}
            />
          </div>

          <div className="section-header">
            <p>{t.benchmarkTypes}</p>
            <Select
              isMulti
              options={optionsBenchTypes}
              value={selectedBenchTypes}
              onChange={setSelectedBenchTypes}
              className="benchmark-filter-testid"
              classNamePrefix="react-select"
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
          <button className="btn-blue" onClick={() => handleRefresh()}>Search</button>
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
                        if (url !== null) handleSVGExport(url, null); // TODO
                      }
                    : () => {
                        const url = constructDownloadURL([exportFile.id]);
                        if (url !== null) handleSVGExport(url, exportFile.id);
                      }
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
