import downloadIcon from '../assets/download.png';
import visualIcon from '../assets/investigate.png';
import { LanguageContext } from '../main.jsx';
import { useContext } from 'react';

/**
 * File table entry component for the user screen
 *
 * @param fileId the id of the file
 * @param filename name of the file
 * @param department department of the user
 * @param time time of conversion
 * @param onExport callback to trigger the export popup
 * @param onVisualize callback to trigger the visualization popup
 * @param showCheckbox whether the textbox should be shown or not (true for admin, false for user)
 * @returns {JSX.Element} the rendered file table entry component
 * @constructor FileTableEntry
 */
const FileTableEntry = ({ fileId, filename, department, time, onExport, onVisualize, showCheckbox }) => {
  const t = useContext(LanguageContext);

  const handleDownload = async () => {
    console.log('downloading file: ' + fileId);
    let response;
    try {
      response = await fetch(`/api/files/${fileId}`);
    }
    catch (error) {
      handleFetchError(error, 'file download');
      return;
    }

    if (!response.ok) {
      handleServerError(response, 'file download');
      return;
    }

    let file;
    try {
      file = await response.blob();
    }
    catch (error) {
      handleBlobError(error, 'file download');
      return;
    }

    const downloadUrl = window.URL.createObjectURL(file);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(downloadUrl);
  };

  function handleServerError(response, context = 'operation') {
    console.error(`Error during ${context}:`, response);
    switch (response.status) {
      case 400:
        alert('Invalid file id. Please check the file and try again.');
        break;
      case 404:
        alert('File not found. It might have been deleted or the ID is wrong.');
        break;
      case 500:
        alert('Server error occurred. Please try again later.');
        break;
      default:
        alert(`Download failed: ${response.statusText}. Please try again.`);
    }
  }

  function handleFetchError(error, context = 'operation') {
    console.error(`Error during ${context}:`, error);
    if (error.name === 'AbortError') {
      alert(`${context} was cancelled. Please try again.`);
    }
    else if (error instanceof TypeError) {
      alert(`Network error during ${context}. Please check your internet connection and try again.`);
    }
    else {
      alert(`Failed to complete ${context}. Please try again.`);
    }
  }

  function handleBlobError(error, context = 'operation') {
    if (error instanceof DOMException) {
      console.log(`${context} was cancelled by the user.`);
    }
    else {
      console.error(`Error decoding response during ${context}:`, error);
      alert('Error accessing or decoding response body. Please try again.');
    }
  }

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
        <button className="btn-green" onClick={handleDownload}>
          <img src={downloadIcon} alt="download" className="icon" />
          {t.download}
        </button>
        <iframe id={fileId}></iframe>
      </td>
    </tr>
  );
};

export default FileTableEntry;
