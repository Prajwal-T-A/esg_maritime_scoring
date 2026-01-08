/**
 * Application Entry Point
 * Renders the React app into the DOM
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App.jsx';

// Get root DOM element
const root = ReactDOM.createRoot(document.getElementById('root'));

// Render React app
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
