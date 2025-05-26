import downloadIcon from '../assets/download.png';
import visualIcon from '../assets/investigate.png';

/**
 * File table entry component for the user screen
 *
 * @param filename name of the file
 * @param department department of the user
 * @param time time of conversion
 * @param onVisualize callback to trigger the visualization popup
 * @param onDownload callback to trigger the download
 * @param t the translation mapping
 * @param showCheckbox whether or not the checkbox must be displayed -- only for admins
 * @returns {JSX.Element} the rendered file table entry component
 * @constructor FileTableEntry
 */
const FileTableEntry = ({ fileId, filename, department, time, onVisualize, t, showCheckbox }) => {
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
  /**
   * Handles a server error if it presents itself during the download process.
   *
   * @param response - the response provided by the server
   * @param context - the context for the error, in this case 'file download'
   */
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
  /**
   * Handles a fetch error if it presents itself during the download process.
   *
   * @param error - the error provided by the server
   * @param context - the context for the error, in this case 'file download'
   */
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
  /**
   * Handles a blob error if it presents itself during the download process.
   *
   * @param error - the error provided by the server
   * @param context - the context for the error, in this case 'file download'
   */
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
        <button className="btn-blue" onClick={onVisualize}>
          <img src={visualIcon} alt="visualize" className="icon" />
          {t.visualize}
        </button>
        <button className="btn-green" onClick={handleDownload}>
          <img src={downloadIcon} alt="download" className="icon" />
          {t.download}
        </button>
      </td>
    </tr>
  );
};

export default FileTableEntry;
