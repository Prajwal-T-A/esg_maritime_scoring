/**
 * Main App Component
 * Entry point for the React application
 * 
 * Sets up React Router for navigation
 * Currently has only Home page, but router is ready for additional pages
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home.jsx';

function App() {
  return (
    <Router>
      <Routes>
        {/* Home Page - Main route */}
        <Route path="/" element={<Home />} />
        
        {/* Future routes can be added here */}
        {/* Example: <Route path="/about" element={<About />} /> */}
      </Routes>
    </Router>
  );
}

export default App;
