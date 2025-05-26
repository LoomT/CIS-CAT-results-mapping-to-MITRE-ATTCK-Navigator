import downloadIcon from '../assets/download.png';
import visualIcon from '../assets/investigate.png';

/**
 * File table entry component for the user screen
 *
 * @param id the id of the file
 * @param filename name of the file
 * @param department department of the user
 * @param size the size of the file
 * @param time time of conversion
 * @param onExport callback to trigger the export popup
 * @param onVisualize callback to trigger the visualization popup
 * @param onDownload callback to trigger the download
 * @param t the translation mapping
 * @returns {JSX.Element} the rendered file table entry component
 * @constructor FileTableEntry
 */
const FileTableEntry = ({ id, filename, department, time, onExport, onVisualize, onDownload, t, showCheckbox }) => {
  return (
    <tr>
      {showCheckbox && (
        <td>
          <input type="checkbox" />
        </td>
      )}
      <td>{filename}</td>
      <td>{department}</td>
      <td>{time}</td>
      <td>
        <button className="btn-blue" onClick={onExport}>
          <img src={visualIcon} alt="export" className="icon" />
          {t.export}
        </button>
        <button className="btn-blue" onClick={onVisualize}>
          <img src={visualIcon} alt="visualize" className="icon" />
          {t.visualize}
        </button>
        <button className="btn-green" onClick={onDownload}>
          <img src={downloadIcon} alt="download" className="icon" />
          {t.download}
        </button>
        <iframe id={id}></iframe>
      </td>
    </tr>
  );
};

export default FileTableEntry;
