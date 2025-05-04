import React from 'react';
import './UserScreen.css';

function UserScreen() {
  return (
    <div className="user-screen">
      <div className="upload-section">
        <h2>Upload a File</h2>
        <button className="upload-button">Upload File</button>
      </div>

      <div className="file-table-section">
        <h2>Files List</h2>
        <table className="file-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Department</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {/* Placeholders, TODO for later*/}
            <tr>
              <td>File 1</td>
              <td>Department 1</td>
              <td>Date</td>
              <td>
                <button className="view-button">Visualize</button>
                <button className="download-button">Download</button>
              </td>
            </tr>
            <tr>
              <td>File 2</td>
              <td>Department 2</td>
              <td>Date</td>
              <td>
                <button className="view-button">Visualize</button>
                <button className="download-button">Download</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default UserScreen;
