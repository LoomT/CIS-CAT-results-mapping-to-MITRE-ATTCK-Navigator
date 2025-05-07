import React from 'react';
import './HomeScreen.css';

/**
 * DemoChoiceScreen Component
 * --------------------------
 * The entry screen of the application where users choose between Demo 1 and Demo 2 modes.
 *
 * Props:
 * - onDemo1Click (function): Callback invoked when the "Demo 1" button is clicked.
 * - onDemo2Click (function): Callback invoked when the "Demo 2" button is clicked.
 */
function DemoChoiceScreen({ onDemo1Click, onDemo2Click }) {
  return (
    <div className="home-screen">
      <h2>Choose a demo</h2>

      {/* Buttons for demo selection */}
      <div className="button-container">
        <button className="button" onClick={onDemo1Click}>Demo 1</button>
        <button className="button" onClick={onDemo2Click}>Demo 2</button>
      </div>
    </div>
  );
}

export default DemoChoiceScreen;
