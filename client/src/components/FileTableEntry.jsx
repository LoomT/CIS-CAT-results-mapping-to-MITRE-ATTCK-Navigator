import downloadIcon from '../assets/download.png';
import visualIcon from '../assets/investigate.png';
import { LanguageContext } from '../main.jsx';
import { useContext, useState } from 'react';

/**
 * File table entry component for the user screen
 *
 * @param fileId the id of the file
 * @param filename name of the file
 * @param department department of the user
 * @param time time of conversion
 * @param onExport callback to trigger the export popup
 * @param onVisualize callback to trigger the visualization popup
 * @param onDownload callback to trigger the download
 * @param showCheckbox whether the textbox should be shown or not (true for admin, false for user)
 * @param onCheckboxChange callback to trigger when the checkbox is changed
 * @param isAllFilesChecked boolean indicating if all files in the table are checked (used for "Select All" functionality)
 * @returns {JSX.Element} the rendered file table entry component
 * @constructor FileTableEntry
 */
const FileTableEntry = ({
  fileId,
  filename,
  department,
  time,
  onExport,
  onVisualize,
  onDownload,
  showCheckbox,
  onCheckboxChange,
  isAllFilesChecked,
}) => {
  const t = useContext(LanguageContext);
  const [isChecked, setIsChecked] = useState(false);

  return (
    <tr>
      {showCheckbox && (
        <td>
          <input
            type="checkbox"
            checked={isAllFilesChecked ? true : isChecked}
            onChange={() => {
              setIsChecked(!isChecked);
              onCheckboxChange(isChecked, fileId);
            }}
            disabled={isAllFilesChecked}
          />
        </td>
      )}
      <td className="long-word">{filename}</td>
      <td><div className="department-badge">{department}</div></td>
      <td className="long-word">{time}</td>
      <td>
        <div className="button-container">
          <button className="btn-purple" onClick={onExport}>
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
          <iframe id={fileId}></iframe>
        </div>
      </td>
    </tr>
  );
};

export default FileTableEntry;
