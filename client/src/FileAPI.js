import NavigatorAPI from './NavigatorAPI.js';

/**
 * Constructs a download URL based on the provided file ids.
 *
 * This function generates a URL endpoint tailored to download one or multiple files.
 * If no files are provided, an alert is triggered notifying the user and null is returned.
 * For a single file, the function modifies the URL to point to a specific file endpoint.
 * For multiple files, it sets up query parameters with file IDs and points to an aggregate endpoint.
 *
 * @function
 * @param {Array<String>} fileIds - An array of file ids.
 * @returns {URL|null} A URL object pointing to the constructed download endpoint or null if no files are provided.
 */
export function constructDownloadURL(fileIds) {
  const uri = new URL(location.href);
  if (fileIds.length === 0) {
    console.error('No files selected!');
    alert('No files selected!');
    return null;
  }
  else if (fileIds.length === 1) {
    // Use special endpoint for single file download
    const id = fileIds[0];
    uri.pathname = `/api/files/${id}`;
  }
  else {
    fileIds.forEach(id => uri.searchParams.append('id', id));
    uri.pathname = `/api/files/aggregate`;
  }
  console.log('constructed URL for fetching files: ' + uri.toString());
  return uri;
}

/**
 * Asynchronously handles downloading a file from the given URI and saves it with the specified filename.
 *
 * This function attempts to fetch the resource from the provided URI, processes the response,
 * and triggers a client-side download for the fetched file. Additionally, it handles errors
 * that may occur during the fetch process or response handling.
 *
 * Error handling includes:
 * - Network-related issues, such as aborting or connectivity errors.
 * - Specific HTTP response status matching (e.g., 400, 404, 500).
 * - Issues decoding or accessing the response body.
 *
 * The function also attempts to extract the actual filename from the `Content-Disposition` header
 * of the response (if it exists), or uses the supplied `filename` parameter otherwise.
 *
 * @async
 * @function
 * @param {URL} uri - The URL of the resource to be downloaded.
 * @param {string} filename - The desired name for the downloaded file, if no filename is specified in the response headers.
 * @returns {void}
 */
export async function handleDownload(uri, filename) {
  let response;
  try {
    response = await fetch(uri);
  }
  catch (error) {
    console.error('Error downloading file:', error);
    if (error.name === 'AbortError') {
      alert('Downloading was cancelled. Please try again.');
    }
    else if (error instanceof TypeError) {
      alert('Network error occurred. Please check your internet connection and try again.');
    }
    else {
      // Fallback for unknown errors
      alert('Failed to download file. Please try again.');
    }
    return;
  }

  if (!response.ok) {
    console.error('Error downloading file:', response);
    switch (response.status) {
      case 400:
        alert('Invalid file id');
        break;
      case 404:
        alert('File not found');
        break;
      case 500:
        alert('Server error occurred while downloading the file. Please try again later.');
        break;
      default:
        alert(`Download failed: ${response.statusText}. Please try again.`);
    }
    return;
  }

  // Get the converted file from the response
  let file;
  try {
    file = await response.blob();
  }
  catch (error) {
    if (error instanceof DOMException) {
      console.log('Download was cancelled by the user.');
    }
    else {
      // Fallback for unknown errors
      console.error('Error accessing or decoding response body:', error);
      alert('Error accessing or decoding response body. Please try again.');
    }
    return;
  }

  // Get filename from the Content-Disposition header if available
  const contentDisposition = response.headers.get('Content-Disposition');

  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
    if (filenameMatch && filenameMatch[1]) {
      filename = filenameMatch[1];
    }
  }

  // Create a download link for the modified file
  const downloadUrl = window.URL.createObjectURL(file);

  // Create a temporary link and trigger download
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(downloadUrl);
}

/**
 * Asynchronously fetches metadata for files from the server.
 *
 * This function makes a `GET` request to the `/api/files/` endpoint to retrieve metadata for files.
 * It uses error handling mechanisms to manage network errors, response decoding issues, and other exceptions.
 *
 * The function handles the following scenarios:
 * - Network errors such as connection loss or fetch cancellation.
 * - Server-side issues such as HTTP 500 errors.
 * - Issues with decoding or accessing the response body.
 *
 * If the fetch operation succeeds and the response can be properly decoded, it logs the retrieved file metadata and returns it.
 * Otherwise, it displays appropriate error messages to the user and logs the errors to the console.
 *
 * @async
 * @function
 * @returns {Promise<Object[]|void>} A promise that resolves to an array of file metadata objects if successful, or `void` if an error occurs.
 */
export async function fetchFilesMetadata() {
  let response;
  try {
    response = await fetch('/api/files/');
  }
  catch (error) {
    console.error('Error refreshing files:', error);
    if (error.name === 'AbortError') {
      alert('Refresh was cancelled. Please try again.');
    }
    else if (error instanceof TypeError) {
      alert('Network error occurred. Please check your internet connection and try again.');
    }
    else {
      // Fallback for unknown errors
      alert('Failed to refresh files. Please try again.');
    }
    return;
  }
  if (!response.ok) {
    // Only 500 is possible for this endpoint at the moment
    console.error('Error fetching files:', response);
    alert('Server error occurred while refreshing the files. Please try again later.');
    return;
  }
  let result;
  try {
    result = await response.json();
  }
  catch (error) {
    console.error('Error downloading file:', error);
    if (error instanceof DOMException) {
      console.log('Refresh was cancelled by the user.');
    }
    else {
      // Fallback for unknown errors
      console.error('Error accessing or decoding response body:', error);
      alert('Error accessing or decoding response body. Please try again.');
    }
    return;
  }

  console.log(result);

  return result;
}

/**
 * Opens the visualization popup.
 */
export const handleVisualize = (uri) => {
  let targetWindow = window.open('/attack-navigator/index.html');

  let client = new NavigatorAPI(targetWindow, uri.toString(), false);
};

/**
 * Handle SVG export & download
 */
export function handleSVGExport(uri, id) {
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
  newIframe.id = id; // TODO @Qyn what IFrame to use when aggregating?

  let frame = document.getElementById(id);
  frame.parentNode.replaceChild(newIframe, frame);

  let targetWindow = newIframe.contentWindow;

  let client = new NavigatorAPI(targetWindow, uri.toString(), true);
}

/**
 * Handles file upload to the server and returns the generated file id.
 *
 * @async
 * @function
 * @param file {Object} - The file to be uploaded.
 * @returns {Promise<Object|null>} - A promise with the file id that resolves when the file is uploaded.
 */
export async function handleFileUpload(file) {
  const formData = new FormData();
  formData.append('file', file);

  console.log('uploading file: ' + formData);
  let response;
  try {
    response = await fetch('/api/files/', {
      method: 'POST',
      body: formData,
    });
  }
  catch (error) {
    // TODO maybe try doing the fetch a few times before failing on some type of errors?
    if (error instanceof DOMException && error.name === 'AbortError') {
      console.log('Upload was cancelled by the user.');
    }
    else if (error instanceof TypeError) {
      console.error('Error uploading file:', error);
      alert('Network error occurred. Please check your internet connection and try again.');
    }
    else {
      // Fallback for unknown errors
      console.error('Error uploading file:', error);
      alert('Failed to upload file. Please try again.');
    }
    return null;
  }

  if (!response.ok) {
    console.error('Error uploading file:', response);
    switch (response.status) {
      case 400:
        alert('Invalid file format or empty file. Please ensure you\'re uploading a valid JSON file.');
        break;
      case 500:
        alert('Server error occurred while processing the file. Please try again later.');
        break;
      default:
        alert(`Upload failed: ${response.statusText}. Please try again.`);
    }
    return null;
  }
  let data;
  try {
    data = await response.json();
  }
  catch (error) {
    if (error instanceof DOMException) {
      console.log('Upload was cancelled by the user.');
    }
    else if (error instanceof SyntaxError) {
      console.error('Error parsing JSON:', error);
      alert('Response from server is not valid JSON. Please try again.');
    }
    else {
      // Fallback for unknown errors
      console.error('Error accessing or decoding response body:', error);
      alert('Error accessing or decoding response body. Please try again.');
    }
    return null;
  }

  console.log('File uploaded successfully. File ID:', data.id);

  return data;
}
