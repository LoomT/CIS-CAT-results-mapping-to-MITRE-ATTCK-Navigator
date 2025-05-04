import React from 'react';
import './AdminOverview.css';

function AdminOverview() {
  return (
    <div className="admin-overview">
      {/* Top Navigation Bar */}
      <div className="top-bar">
        <div className="back-text" onClick={() => window.history.back()}>← Back</div>
        <div className="title-text">Admin Overview</div>
      </div>

      {/* Placeholder Content */}
      <div className="overview-content">
        <h2>Welcome to the Admin Overview</h2>
        <p>This is a placeholder screen for the Admin Overview. You can add content here later, such as stats, management tools, etc.</p>

        <div className="admin-actions">
          <button className="action-button">Action 1</button>
          <button className="action-button">Action 2</button>
          <button className="action-button">Action 3</button>
        </div>
      </div>
    </div>
  );
}

export default AdminOverview;
