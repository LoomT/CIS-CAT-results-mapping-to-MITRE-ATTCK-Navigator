import NavigatorAPI from './NavigatorAPI.js';
import { jsPDF } from 'jspdf';
import 'svg2pdf.js';

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
export function constructDownloadURLFromFileIds(fileIds) {
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
 * Constructs a download URL based on the provided query parameters.
 *
 * @param {string} filename - The name of the file to download.
 * @param {Array<string>} departments - List of department names to filter the data.
 * @param {Array<string>} benchmarks - List of benchmarks to filter the data.
 * @param {Array<string>} hostnames - List of hostnames to filter the data.
 * @param {string} dateFrom - The start date for the data query in ISO format.
 * @param {string} dateTo - The end date for the data query in ISO format.
 * @return {URL} A URL object representing the constructed download URL.
 */
export function constructDownloadURLFromQueryParams(
  filename,
  departments,
  benchmarks,
  hostnames,
  dateFrom,
  dateTo,
) {
  const url = new URL(location.href);
  url.pathname = '/api/files/aggregate';
  const queryParams = constructQueryParams(
    filename,
    departments,
    benchmarks,
    hostnames,
    dateFrom,
    dateTo,
  );
  queryParams.forEach((value, key) => url.searchParams.append(key, value));
  console.log('constructed URL for fetching files: ' + url.toString());
  return url;
}

/**
 * Constructs query parameters based on the given inputs and returns them as a URLSearchParams object.
 *
 * @param {string} filename - The filename to be used as a search query. If empty, no filename parameter is added.
 * @param {string[]} departments - An array of department names to filter by. Each department is added as a separate parameter.
 * @param {string[]} benchmarks - An array of benchmark identifiers to filter by. Each benchmark is added as a separate parameter.
 * @param {string[]} hostnames - An array of hostnames to filter by. Each hostname is added as a separate parameter.
 * @param {string} dateFrom - The starting date and time for the filter in 'YYYY-MM-DDTHH:MM:SS' format. If empty, no minimum time parameter is added.
 * @param {string} dateTo - The ending date and time for the filter in 'YYYY-MM-DDTHH:MM:SS' format. If empty, no maximum time parameter is added.
 * @return {URLSearchParams} A URLSearchParams object containing the constructed query parameters.
 */
function constructQueryParams(
  filename = '',
  departments = [],
  benchmarks = [],
  hostnames = [],
  dateFrom = '',
  dateTo = '',
) {
  const queryParams = new URLSearchParams();
  if (filename.length > 0) {
    queryParams.append('search', filename);
  }
  if (departments.length > 0) {
    departments.forEach(department => queryParams.append('department', department));
  }
  if (benchmarks.length > 0) {
    benchmarks.forEach(benchmark => queryParams.append('benchmark', benchmark));
  }
  if (hostnames.length > 0) {
    hostnames.forEach(hostname => queryParams.append('hostname', hostname));
  }
  if (dateFrom.length > 0) {
    dateFrom = dateFrom.concat(':00Z');
    queryParams.append('min_time', dateFrom);
  }
  if (dateTo.length > 0) {
    dateTo = dateTo.concat(':00Z');
    queryParams.append('max_time', dateTo);
  }
  return queryParams;
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
    if (error instanceof DOMException && error.name === 'AbortError') {
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
    if (error instanceof DOMException && error.name === 'AbortError') {
      alert('Downloading was cancelled. Please try again.');
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
 * Asynchronously fetches ids for files from the server.
 *
 * This function makes a `GET` request to the `/api/files/` endpoint to retrieve all ids of files.
 *
 * If the fetch operation succeeds and the response can be properly decoded, it logs the retrieved file ids and returns them.
 * Otherwise, it displays appropriate error messages to the user and logs the errors to the console.
 *
 * @async
 * @function
 * @param {string} filename - The filename to be used as a search query. If empty, no filename parameter is added.
 * @param {string[]} departments - An array of department names to filter by. Each department is added as a separate parameter.
 * @param {string[]} benchmarks - An array of benchmark identifiers to filter by. Each benchmark is added as a separate parameter.
 * @param {string[]} hostnames - An array of hostnames to filter by. Each hostname is added as a separate parameter.
 * @param {string} dateFrom - The starting date and time for the filter in 'YYYY-MM-DDTHH:MM:SS' format. If empty, no minimum time parameter is added.
 * @param {string} dateTo - The ending date and time for the filter in 'YYYY-MM-DDTHH:MM:SS' format. If empty, no maximum time parameter is added.
 * @returns {Promise<Object|null>} A promise that resolves to an object with file id list if successful, or `null` if an error occurs.
 */
export async function fetchFilesIDs(
  filename = '',
  departments = [],
  benchmarks = [],
  hostnames = [],
  dateFrom = '',
  dateTo = '',
) {
  let response;
  try {
    const queryParams = constructQueryParams(
      filename,
      departments,
      benchmarks,
      hostnames,
      dateFrom,
      dateTo,
    );

    const url = new URL(location.href);
    url.pathname = '/api/files';
    queryParams.forEach((value, key) => url.searchParams.append(key, value));
    console.log('fetching files ids from: ' + url.toString());
    response = await fetch(url);
  }
  catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      return null; // Abort fetch
    }
    console.error('Error refreshing files:', error);
    if (error instanceof TypeError) {
      alert('Network error occurred. Please check your internet connection and try again.');
    }
    else {
      // Fallback for unknown errors
      alert('Failed to refresh files. Please try again.');
    }
    return null;
  }
  if (!response.ok) {
    // Only 500 is possible for this endpoint at the moment
    console.error('Error fetching files:', response);
    alert('Server error occurred while refreshing the files. Please try again later.');
    return null;
  }
  let ids;
  try {
    ids = (await response.json()).ids;
  }
  catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      return null;
    }
    else {
      // Fallback for unknown errors
      console.error('Error accessing or decoding response body:', error);
      alert('Error accessing or decoding response body. Please try again.');
    }
    return null;
  }

  console.log(ids);

  return ids;
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
 * @param {int} page - The page number for pagination, starting from 0.
 * @param {int} pageSize - The number of items to return per page.
 * @param {string} filename - The filename to be used as a search query. If empty, no filename parameter is added.
 * @param {string[]} departments - An array of department names to filter by. Each department is added as a separate parameter.
 * @param {string[]} benchmarks - An array of benchmark identifiers to filter by. Each benchmark is added as a separate parameter.
 * @param {string[]} hostnames - An array of hostnames to filter by. Each hostname is added as a separate parameter.
 * @param {string} dateFrom - The starting date and time for the filter in 'YYYY-MM-DDTHH:MM:SS' format. If empty, no minimum time parameter is added.
 * @param {string} dateTo - The ending date and time for the filter in 'YYYY-MM-DDTHH:MM:SS' format. If empty, no maximum time parameter is added.
 * @param {AbortSignal} signal - The signal object that allows you to abort a DOM request.
 * @returns {Promise<Object|null>} A promise that resolves to an object with file metadata if successful, or `null` if an error occurs.
 */
export async function fetchFilesMetadata(
  page = 0,
  pageSize = 20,
  filename = '',
  departments = [],
  benchmarks = [],
  hostnames = [],
  dateFrom = '',
  dateTo = '',
  signal = null,
) {
  let response;
  try {
    const queryParams = constructQueryParams(
      filename,
      departments,
      benchmarks,
      hostnames,
      dateFrom,
      dateTo,
    );

    // Add pagination parameters
    queryParams.append('page', page.toString());
    queryParams.append('page_size', pageSize.toString());

    const url = new URL(location.href);
    url.pathname = '/api/files';
    queryParams.forEach((value, key) => url.searchParams.append(key, value));
    url.searchParams.append('verbose', 'true');
    console.log('fetching files metadata from: ' + url.toString());
    response = await fetch(url, { signal });
  }
  catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      return null; // Abort fetch
    }
    console.error('Error refreshing files:', error);
    if (error instanceof TypeError) {
      alert('Network error occurred. Please check your internet connection and try again.');
    }
    else {
      // Fallback for unknown errors
      alert('Failed to refresh files. Please try again.');
    }
    return null;
  }
  if (!response.ok) {
    // Only 500 is possible for this endpoint at the moment
    console.error('Error fetching files:', response);
    alert('Server error occurred while refreshing the files. Please try again later.');
    return null;
  }
  let result;
  try {
    result = await response.json();
  }
  catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      return null;
    }
    else {
      // Fallback for unknown errors
      console.error('Error accessing or decoding response body:', error);
      alert('Error accessing or decoding response body. Please try again.');
    }
    return null;
  }

  console.log(result);

  return result;
}

/**
 * Opens the visualization popup.
 */
export const handleVisualize = (uri) => {
  let linkFragment = '#layerURL=' + encodeURIComponent(uri);
  window.open('/attack-navigator/index.html' + linkFragment);
};

/**
 * Creates a fresh iframe with NavigatorAPI client
 *
 * Dirty workaround to get a fresh handle to the iframe window.
 * There are a couple of issues with reusing the old one,
 * specifically that navigation takes time. A lot of time.
 * So when we modify the src the window will still point to the
 * old window object. There's definitely a better solution than this
 * but let's mark this as TODO.
 */
function createNavigatorClient(uri, id) {
  const newIframe = document.createElement('iframe');
  newIframe.sandbox = 'allow-scripts allow-same-origin allow-downloads';
  newIframe.src = '/attack-navigator/index.html';
  newIframe.id = id;

  let frame = document.getElementById(id);
  frame.parentNode.replaceChild(newIframe, frame);

  let targetWindow = newIframe.contentWindow;
  return new NavigatorAPI(targetWindow, uri.toString());
}

/**
 * Get the SVG representing this uri
 */
export async function getSVG(uri, id) {
  const client = createNavigatorClient(uri, id);
  return await client.getSVG();
}

/**
 * Handle SVG export & download
 */
export async function handleSVGExport(uri, id) {
  const client = createNavigatorClient(uri, id);
  return await client.downloadSVG();
}

/**
 * Handle PDF export & download with each SVG on separate page
 */
export async function handlePDFExport(uris, ids) {
  let promises = [];

  for (let i = 0; i < ids.length; i++) {
    let svgPromise = getSVG(uris[i], ids[i]);
    promises.push(svgPromise);
  }
  let svgElements;
  try {
    // Wait for all SVGs to be retrieved and store the results
    svgElements = await Promise.all(promises);
  }
  catch {
    alert('Failed to retrieve all SVGs');
    return;
  }
  if (svgElements.length === 0) {
    throw new Error('No SVG elements retrieved');
  }

  // Use the first SVG to initialize the PDF document
  const firstSvg = svgElements[0];
  const firstWidth = firstSvg.width.baseVal.value;
  const firstHeight = firstSvg.height.baseVal.value;

  const doc = new jsPDF(firstWidth > firstHeight ? 'l' : 'p', 'pt', [firstWidth, firstHeight]);

  // Add each SVG to the PDF
  for (let i = 0; i < svgElements.length; i++) {
    const svgElement = svgElements[i];
    const width = svgElement.width.baseVal.value;
    const height = svgElement.height.baseVal.value;

    // Add new page for subsequent SVGs
    if (i > 0) {
      doc.addPage([width, height], width > height ? 'l' : 'p');
    }

    // Add SVG to current page
    await doc.svg(svgElement, {
      x: 0,
      y: 0,
      width,
      height,
    });
  }

  // Save the PDF with all SVGs
  doc.save(`combined_svgs_${ids.length}_items.pdf`);
}

/**
 * Handles file upload to the server and returns the generated file id.
 *
 * @async
 * @function
 * @param file {Object} - The file to be uploaded.
 * @returns {Promise<Object|null>} - A promise with the file id that resolves when the file is uploaded.
 */
export async function handleFileUpload(file, departmentId) {
  const formData = new FormData();
  formData.append('file', file);

  console.log('uploading file: ' + formData);
  let response;
  try {
    response = await fetch(`/api/files/?department_id=${encodeURIComponent(departmentId)}`, {
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
    if (error instanceof DOMException && error.name === 'AbortError') {
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
