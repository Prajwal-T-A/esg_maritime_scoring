/**
 * Main App Component
 * Entry point for the React application
 * 
 * Routes:
 * - / : Landing page with project introduction
 * - /analyze : Vessel analysis page with ML + ESG scoring
 * - /legacy : Original Home page (kept for reference)
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing.jsx';
import AnalyzeVessel from './pages/AnalyzeVessel.jsx';
import Home from './pages/Home.jsx';
import Chatbot from './components/Chatbot.jsx';

function App() {
  return (
    <Router>
      <Routes>
        {/* Landing Page - New main route */}
        <Route path="/" element={<Landing />} />
        
        {/* Analyze Vessel Page */}
        <Route path="/analyze" element={<AnalyzeVessel />} />
        
        {/* Legacy Home Page - kept for reference */}
        <Route path="/legacy" element={<Home />} />
      </Routes>
      
      {/* Global Chatbot - available on all pages */}
      <Chatbot />
    </Router>
  );
}

export default App;
