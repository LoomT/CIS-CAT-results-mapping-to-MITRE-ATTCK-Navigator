import React, { useContext, useEffect, useRef, useState } from 'react';
import Select from 'react-select';
import './globalstyle.css';
import FileTableEntry from './components/FileTableEntry.jsx';
import { LanguageContext } from './main.jsx';
import {
  constructDownloadURLFromFileIds,
  constructDownloadURLFromQueryParams,
  fetchFilesMetadata,
  handleDownload,
  handlePDFExport,
  handleSVGExport,
  handleVisualize,
} from './FileAPI.js';

// used for scroll-to-bottom event
const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

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
  const [isAllFilesChecked, setAllFilesChecked] = useState(false);
  const [optionsDepts, setOptionsDepts] = useState([]);
  const [selectedDepts, setSelectedDepts] = useState([]);
  const [activeDepts, setActiveDepts] = useState([]);
  const [optionsBenchTypes, setOptionsBenchTypes] = useState([]);
  const [selectedBenchTypes, setSelectedBenchTypes] = useState([]);
  const [activeBenchTypes, setActiveBenchTypes] = useState([]);
  const [optionsHosts, setOptionsHosts] = useState([]);
  const [selectedHosts, setSelectedHosts] = useState([]);
  const [activeHosts, setActiveHosts] = useState([]);
  const [searchText, setSearchText] = useState('');
  const [activeSearchText, setActiveSearchText] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [activeDateFrom, setActiveDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [activeDateTo, setActiveDateTo] = useState('');

  const [totalNumberOfFiles, setTotalNumberOfFiles] = useState(0);
  const [currentPage, setCurrentPage] = useState(0);
  const [hasMoreFiles, setHasMoreFiles] = useState(false);
  const [pageSize] = useState(20);
  const loadMoreAbortController = useRef(null);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [isSearching, setIsSearching] = useState(true);

  const t = useContext(LanguageContext);

  useEffect(() => {
    // Load the options for the dropdowns when the component mounts
    fetchFilesMetadata(0, pageSize).then((result) => {
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

  useEffect(() => {
    if (!hasMoreFiles) return; // don't register the scroll listener if there are no files left to load
    const handleScroll = debounce(() => {
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;

      // Check if user has scrolled to near the bottom (within 100px)
      if (scrollTop + windowHeight >= documentHeight - 100) {
        loadMoreFiles();
      }
    }, 100);

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isLoadingMore, isSearching, hasMoreFiles, currentPage, activeSearchText, activeDepts, activeBenchTypes, activeHosts, activeDateFrom, activeDateTo]);

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
   * Asynchronous function to handle the refresh operation for the file table.
   *
   * This function fetches metadata for files if a result parameter is not provided
   * or processes a provided result object. The used search parameters are set as active
   * for loading next pages such that newly selected options don't take effect until search is pressed.
   *
   * Will abort `loadMoreFiles` fetch operation if it was ongoing.
   *
   * @async
   * @function
   * @param {Object|null} [result=null] - Optional result data containing metadata of files.
   * If no result is provided, the function will fetch data using `fetchFilesMetadata`.
   * @return {Promise<void>} Resolves when the loading process is complete. Returns nothing explicitly.
   */
  async function handleRefresh(result = null) {
    // Cancel any ongoing loadMoreFiles request
    if (loadMoreAbortController.current) {
      loadMoreAbortController.current.abort();
      loadMoreAbortController.current = null;
    }

    setIsSearching(true);
    setCurrentPage(0);

    if (result === null) {
      result = await fetchFilesMetadata(
        0,
        pageSize,
        searchText,
        selectedDepts.map(dept => dept.value),
        selectedBenchTypes.map(bench => bench.value),
        selectedHosts.map(host => host.value),
        dateFrom,
        dateTo,
      );
    }
    if (result === null) {
      setIsSearching(false);
      return;
    }

    setFiles(result.data.map(file => ({
      id: file.id,
      filename: file.filename,
      department: file.department ? file.department.name : 'None',
      time: file.time_created ? file.time_created.replace('T', ' ') : null,
    })));

    // lock in the active search parameters
    // to be able to load more pages using these
    setActiveSearchText(searchText);
    setActiveDepts(selectedDepts.map(dept => dept.value));
    setActiveBenchTypes(selectedBenchTypes.map(bench => bench.value));
    setActiveHosts(selectedHosts.map(host => host.value));
    setActiveDateFrom(dateFrom);
    setActiveDateTo(dateTo);

    setTotalNumberOfFiles(result.pagination.total_count);

    // Check if there are more files to load
    const totalPages = Math.ceil(result.pagination.total_count / pageSize);
    setHasMoreFiles(totalPages > 1);
    setAllFilesChecked(false);
    setIsSearching(false);
  }

  /**
   * Loads additional files metadata and appends it to the existing list of files.
   * Manages the loading state and fetches data based on the current page, active filters, and other parameters.
   * Handles aborting of ongoing requests and checks if more files are available to load.
   *
   * @async
   * @function
   * @return {Promise<void>} Resolves when the loading process is complete. Returns nothing explicitly.
   */
  async function loadMoreFiles() {
    if (isLoadingMore || isSearching || !hasMoreFiles) return;

    if (loadMoreAbortController.current) {
      // Should not happen as filesAreBeingLoaded should have been true
      console.error('Unexpected abort controller in loadMoreFiles: ', loadMoreAbortController.current);
      return;
    }

    loadMoreAbortController.current = new AbortController();
    setIsLoadingMore(true);
    const nextPage = currentPage + 1;

    const result = await fetchFilesMetadata(
      nextPage,
      pageSize,
      activeSearchText,
      activeDepts.map(dept => dept.value),
      activeBenchTypes.map(bench => bench.value),
      activeHosts.map(host => host.value),
      activeDateFrom,
      activeDateTo,
      loadMoreAbortController.current.signal,
    );

    if (result === null) {
      setIsLoadingMore(false);
      loadMoreAbortController.current = null;
      return;
    }

    // Append new files to existing ones
    const newFiles = result.data.map(file => ({
      id: file.id,
      filename: file.filename,
      department: file.department ? file.department.name : 'None',
      time: file.time_created ? file.time_created.replace('T', ' ') : null,
    }));

    setFiles(prevFiles => [...prevFiles, ...newFiles]);
    setCurrentPage(nextPage);

    // Check if there are more files to load
    const totalPages = Math.ceil(result.pagination.total_count / pageSize);
    setHasMoreFiles(nextPage < totalPages - 1);
    setIsLoadingMore(false);
    loadMoreAbortController.current = null;
  }

  /**
   * Constructs a download URL based on the selected files or filters.
   * If no files are selected, the method returns null. If all files are
   * checked, it constructs the URL using the provided query parameters.
   * Otherwise, it generates the URL based on the selected file IDs.
   *
   * @return {URL|null} A download URL as a string, or null if no files
   *         are selected (edge case handled when buttons are disabled).
   */
  function constructAggregateDownloadURL() {
    if (files.length === 0) return null; // should not happen as the buttons are disabled
    else if (isAllFilesChecked) {
      return constructDownloadURLFromQueryParams(
        activeSearchText,
        activeDepts.map(dept => dept.value),
        activeBenchTypes.map(bench => bench.value),
        activeHosts.map(host => host.value),
        activeDateFrom,
        activeDateTo,
      );
    }
    else {
      return constructDownloadURLFromFileIds(selectedFiles);
    }
  }

  return (
    <div className="full-panel">
      {/* Top Title */}
      <div className="user-title">{t.adminOverview}</div>

      {/* Section with selectors (department toggle and search bar) */}
      <div className="content-area">
        <div className="card admin-side-section padded">
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

          {/* TODO in seperate issue */}
          {/* <div className="section-header"> */}
          {/*  <label> */}
          {/*    <p>{t.onlyLatestFiles}</p> */}
          {/*    <input type="checkbox" /> */}
          {/*  </label> */}
          {/* </div> */}

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
          <button
            className="btn-blue"
            onClick={() => handleRefresh()}
            disabled={isSearching}
          >
            {isSearching
              ? (
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <span>Searching</span>
                    <div className="loading-dots">
                      <span className="dot">.</span>
                      <span className="dot">.</span>
                      <span className="dot">.</span>
                    </div>
                  </div>
                )
              : (
                  'Search'
                )}
          </button>

          <p>{'Showing ' + totalNumberOfFiles + ' files'}</p>
          <h2>Aggregation</h2>
          <iframe id="aggregateFrame"></iframe>
          {files.length === 0 || (selectedFiles.length === 0 && !isAllFilesChecked)
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
                  <p>{'Selected files: ' + (isAllFilesChecked ? totalNumberOfFiles : selectedFiles.length)}</p>
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
                          const url = constructAggregateDownloadURL();
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
                          const url = constructAggregateDownloadURL();
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

        {/* File Table Section */}
        <div className="card file-table-section">
          <table>
            <thead>
              <tr>
                <th>
                  <input
                    type="checkbox"
                    checked={isAllFilesChecked}
                    onChange={() => setAllFilesChecked(!isAllFilesChecked)}
                  />
                </th>
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
                      const url = constructDownloadURLFromFileIds([file.id]);
                      if (url !== null) handleVisualize(url);
                    }
                  }
                  onDownload={
                    () => {
                      const url = constructDownloadURLFromFileIds([file.id]);
                      if (url !== null) handleDownload(url, file.filename);
                    }
                  }
                  showCheckbox={true}
                  onCheckboxChange={handleCheckboxChange}
                  isAllFilesChecked={isAllFilesChecked}
                />
              ))}
            </tbody>
          </table>

          {/* Loading indicator */}
          {isLoadingMore && (
            <div className="loading-container">
              <div className="loading-bounce">
                <div></div>
                <div></div>
                <div></div>
              </div>
            </div>
          )}

          {/* End of results indicator */}
          {!hasMoreFiles && files.length > 0 && (
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <p>No more files to load</p>
            </div>
          )}

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
                        const url = constructAggregateDownloadURL();
                        if (url !== null) handleSVGExport(url, 'aggregateFrame');
                      }
                    : () => {
                        const url = constructDownloadURLFromFileIds([exportFile.id]);
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
                          const url = constructAggregateDownloadURL();
                          if (url !== null) handlePDFExport([url], ['aggregateFrame']);
                        }}
                      >
                        Aggregate PDF
                      </button>
                      <button
                        className="popup-button"
                        onClick={() => {
                          //TODO
                          const uris = selectedFiles.map(fileId => constructDownloadURLFromFileIds([fileId]));
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
                        const url = constructDownloadURLFromFileIds([exportFile.id]);
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
