/**
 * File table entry component for the user screen
 *
 * @param filename name of the file
 * @param department department of the user
 * @param time time of conversion
 * @param onVisualize callback to open the MITRE ATT&CK Navigator
 * @param onExport callback to trigger the export popup
 * @param onDownload callback to trigger the download
 * @returns {JSX.Element} the rendered file table entry component
 * @constructor FileTableEntry
 */
const FileTableEntry = ({ filename, department, time, onVisualize, onExport, onDownload }) => {
  return (
    <tr>
      <td>{filename}</td>
      <td>{department}</td>
      <td>{time}</td>
      <td>
        <button className="view-button" onClick={onVisualize}>Visualize</button>
        <button className="export-button" onClick={onExport}>Export</button>
        <button className="download-button" onClick={onDownload}>Download</button>
      </td>
    </tr>
  );
};

export default FileTableEntry;
