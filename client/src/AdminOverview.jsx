import React, { useContext, useState } from 'react';
import { Link } from 'react-router-dom';
import './globalstyle.css';
import backIcon from './assets/back.png';
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
  const [currentFile, setFile] = useState({});
  const [hostSearch, setHostSearch] = useState(''); // TODO: currently unused
  const [files] = useState([]);
  const t = useContext(LanguageContext);

  /**
   * Opens the visualization popup.
   */
  const handleVisualizeClick = () => {
    let uri = new URL(location.href);

    uri.pathname = `/api/files/${file.id}`;
    let targetWindow = window.open('/attack-navigator/index.html');

    let client = new NavigatorAPI(targetWindow, uri.toString(), false);

    setShowPopup(true);
  };

  /**
   * Opens the export popup.
   */
  const handleExportClick = (file) => {
    setFile(file);
    setShowExportPopup(true);
  };

  /**
   * Closes the export popup.
   */
  const handlePopupClose = () => {
    setShowExportPopup(false);
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
    <div className="full-panel">
      {/* Top Title */}
      <div className="user-title">{t.adminOverview}</div>

      {/* Section with selectors (department toggle and search bar) */}
      <div className="content-area">
        <div className="card upload-section">
          <h2>{t.filterFiles}</h2>
          <div className="section-header">
            <p>{t.departmentFilter}</p>
            <select id="departmentFilter" multiple size={3}>
              <option>Department 1</option>
              <option>Department 2</option>
              <option>Department 3</option>
            </select>
          </div>

          <div className="section-header">
            <p>{t.searchHosts}</p>
            <input type="text" placeholder="Search hosts..." />
          </div>

          <div className="section-header">
            <label>
              <p>{t.onlyLatestFiles}</p>
              <input type="checkbox" />
            </label>
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
            <select>
              <option>All Types</option>
              <option>Type 1</option>
              <option>Type 2</option>
              <option>Type 3</option>
            </select>
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
                  onExport={() => handleExportClick(file)}
                  onVisualize={() => handleVisualizeClick(file)}
                  showCheckbox={true}
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
              <button className="popup-button" onClick={handleSVGExportClick()}>SVG</button>
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
