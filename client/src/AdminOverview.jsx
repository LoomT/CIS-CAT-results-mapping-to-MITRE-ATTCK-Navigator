import React, { useContext, useEffect, useRef, useState } from 'react';
import Select from 'react-select';
import downloadIcon from './assets/download.png';
import visualIcon from './assets/investigate.png';
import exportIcon from './assets/export.svg';
import './globalstyle.css';
import FileTableEntry from './components/FileTableEntry.jsx';
import { LanguageContext } from './main.jsx';
import {
  constructDownloadURLFromFileIds,
  constructDownloadURLFromQueryParams,
  fetchFilesIDs,
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
 * - A search and filter section
 * - A list of files with actions for export, visualization and download, and a checkbox to select multiple rows
 * - A popup for choosing export formats (SVG or PDF)
 * - Aggregation menu
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
  const [isExporting, setIsExporting] = useState(false);

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
      time: file.time_created ? new Date(file.time_created).toLocaleString() : null,
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
      activeDepts,
      activeBenchTypes,
      activeHosts,
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
        activeDepts,
        activeBenchTypes,
        activeHosts,
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
      <div className="user-title">{t.reportsOverview}</div>

      {/* Section with selectors (department toggle and search bar) */}
      <div className="content-area">
        <div className="card admin-side-section padded">
          <h2>{t.filterFiles}</h2>
          <div className="section-header">
            <p>{t.searchByFilename}</p>
            <input
              type="text"
              placeholder={t.searchFilenameText}
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
            <p>{t.searchByDepartment}</p>
            <Select
              isMulti
              placeholder={t.select + '...'}
              options={optionsDepts}
              noOptionsMessage={() => t.noOptions}
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
            <p>{t.searchByHost}</p>
            <Select
              isMulti
              placeholder={t.select + '...'}
              options={optionsHosts}
              noOptionsMessage={() => t.noOptions}
              value={selectedHosts}
              onChange={setSelectedHosts}
              className="hostname-filter-testid"
              classNamePrefix="react-select"
            />
          </div>

          <div className="section-header">
            <p>{t.searchByBenchmark}</p>
            <Select
              isMulti
              placeholder={t.select + '...'}
              options={optionsBenchTypes}
              noOptionsMessage={() => t.noOptions}
              value={selectedBenchTypes}
              onChange={setSelectedBenchTypes}
              className="benchmark-filter-testid"
              classNamePrefix="react-select"
            />
          </div>

          <div className="section-header">
            <p>{t.searchByDateRange}</p>
            <p>{t.from}</p>
            <input
              type="datetime-local"
              value={dateFrom}
              onChange={e => setDateFrom(e.target.value)}
            />
            <p>{t.to}</p>
            <input
              type="datetime-local"
              value={dateTo}
              onChange={e => setDateTo(e.target.value)}
            />
          </div>

          <button
            className="btn-blue"
            data-testid="admin-overview-search-button"
            onClick={() => handleRefresh()}
            disabled={isSearching}
          >
            {isSearching
              ? (
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <span>{t.searching}</span>
                    <div className="loading-dots">
                      <span className="dot">.</span>
                      <span className="dot">.</span>
                      <span className="dot">.</span>
                    </div>
                  </div>
                )
              : (
                  t.search
                )}
          </button>

          <p>{t.showNFiles(totalNumberOfFiles)}</p>
          <h2>{t.aggregation}</h2>
          <iframe id="aggregateFrame"></iframe>
          {files.length === 0 || (selectedFiles.length === 0 && !isAllFilesChecked)
            ? (
                <>
                  <p>{t.noFilesSelected}</p>
                  <div className="button-container">
                    <button className="btn-purple" disabled={true}>
                      <img src={exportIcon} alt="export" className="icon" />
                      {t.export}
                    </button>
                    <button className="btn-blue" disabled={true}>
                      <img src={visualIcon} alt="visualize" className="icon" />
                      {t.visualize}
                    </button>
                    <button className="btn-green" disabled={true}>
                      <img src={downloadIcon} alt="download" className="icon" />
                      {t.download}
                    </button>
                  </div>
                </>
              )
            : (
                <>
                  <p>{t.selectedFiles + ': ' + (isAllFilesChecked ? totalNumberOfFiles : selectedFiles.length)}</p>
                  <div className="button-container">
                    <button
                      className="btn-purple"
                      onClick={
                        () => handleExportClick(null, true)
                      }
                    >
                      <img src={exportIcon} alt="export" className="icon" />
                      {t.export}
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
                      <img src={visualIcon} alt="visualize" className="icon" />
                      {t.visualize}
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
                      <img src={downloadIcon} alt="download" className="icon" />
                      {t.download}
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
              <p>{t.noMoreFilesToLoad}</p>
            </div>
          )}

        </div>
      </div>

      {/* Export popup */}
      {/* TODO extract this popup element so it can be reused in here and UserScreen.jsx */}
      {showExportPopup && (
        <div className="popup-overlay">
          <div className="popup">
            {isExporting
              ? (
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <h3 className="popup-heading">{t.exportInProgress}</h3>
                    <div className="loading-dots">
                      <span className="dot">.</span>
                      <span className="dot">.</span>
                      <span className="dot">.</span>
                    </div>
                  </div>
                )
              : (
                  <>
                    <h3 className="popup-heading">{t.chooseFormat}</h3>
                    <div className="button-container">
                      <button
                        className="popup-button"
                        disabled={isExporting}
                        onClick={
                          exportAggregate
                            ? () => {
                                const url = constructAggregateDownloadURL();
                                if (url !== null) {
                                  setIsExporting(true);
                                  handleSVGExport(url, 'aggregateFrame')
                                    .finally(() => setIsExporting(false));
                                }
                              }
                            : () => {
                                const url = constructDownloadURLFromFileIds([exportFile.id]);
                                if (url !== null) {
                                  setIsExporting(true);
                                  handleSVGExport(url, exportFile.id)
                                    .finally(() => setIsExporting(false));
                                }
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
                                disabled={isExporting}
                                onClick={() => {
                                  const url = constructAggregateDownloadURL();
                                  if (url !== null) {
                                    setIsExporting(true);
                                    handlePDFExport([url], ['aggregateFrame'])
                                      .finally(() => setIsExporting(false));
                                  }
                                }}
                              >
                                {t.exportAgrregatePDF}
                              </button>
                              <button
                                className="popup-button"
                                disabled={(isAllFilesChecked && hasMoreFiles) || isExporting} // TODO not loaded in files will not have an iframe for them to be loaded in
                                onClick={() => {
                                  if (!isAllFilesChecked) {
                                    const uris = selectedFiles.map(fileId => constructDownloadURLFromFileIds([fileId]));
                                    if (uris.every(url => url !== null)) {
                                      setIsExporting(true);
                                      handlePDFExport(uris, selectedFiles)
                                        .finally(() => setIsExporting(false));
                                    }
                                  }
                                  else {
                                    setIsExporting(true);
                                    // TODO not loaded in files will not have an iframe for them to be loaded in
                                    fetchFilesIDs(
                                      activeSearchText,
                                      activeDepts,
                                      activeBenchTypes,
                                      activeHosts,
                                      activeDateFrom,
                                      activeDateTo,
                                    ).then((filesToDownload) => {
                                      const uris = filesToDownload.map(fileId => constructDownloadURLFromFileIds([fileId]));
                                      if (uris.every(url => url !== null)) {
                                        handlePDFExport(uris, filesToDownload)
                                          .finally(() => {
                                            setIsExporting(false);
                                          });
                                      }
                                      else {
                                        setIsExporting(false);
                                      }
                                    }, () => setIsExporting(false));
                                  }
                                }}
                              >
                                {t.exportAllPDF}
                              </button>
                            </>
                          )
                        : (
                            <button
                              className="popup-button"
                              disabled={isExporting}
                              onClick={() => {
                                const url = constructDownloadURLFromFileIds([exportFile.id]);
                                if (url !== null) {
                                  setIsExporting(true);
                                  handlePDFExport([url], [exportFile.id])
                                    .finally(() => setIsExporting(false));
                                }
                              }}
                            >
                              PDF
                            </button>
                          )}

                      <button className="popup-cancel" onClick={handlePopupClose}>
                        {t.cancel}
                      </button>
                    </div>
                  </>
                )}
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminOverview;
