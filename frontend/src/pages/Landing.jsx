/**
 * Landing Page Component
 * Welcome page with maritime background and project description
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import maritimeBackground from '../images/maritime-operations-data-analysis.avif';

function Landing() {
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Background Image with Overlay */}
      <div
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{ backgroundImage: `url(${maritimeBackground})` }}
      >
        {/* Dark gradient overlay for text readability */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900/85 via-blue-900/75 to-slate-900/85"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Header */}
        <header className="px-6 py-6">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold text-white tracking-tight">
                Maritime ESG Analytics
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/live')}
                className="text-white hover:text-cyan-300 font-medium transition-colors"
              >
                Live Map
              </button>
              <button
                onClick={() => navigate('/analyze')}
                className="px-6 py-2 bg-white/5 text-white rounded-lg border border-white/30 hover:bg-white/10 transition-all duration-300 font-medium"
              >
                Analyze Vessel
              </button>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 flex items-center justify-center px-6 py-12">
          <div className="max-w-4xl mx-auto text-center space-y-8">
            {/* Hero Title */}
            <div className="space-y-4 animate-fade-in">
              <h2 className="text-5xl md:text-6xl lg:text-7xl font-bold text-white leading-tight">
                Navigate the Future of
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400 mt-2">
                  Sustainable Shipping
                </span>
              </h2>

              <p className="text-xl md:text-2xl text-blue-100 max-w-3xl mx-auto leading-relaxed">
                Advanced ML-powered carbon emission tracking and ESG environmental scoring
                for maritime vessels
              </p>
            </div>

            {/* Feature Cards */}
            <div className="grid md:grid-cols-3 gap-6 mt-12">
              {/* Feature 1 */}
              <div className="group bg-white/5 rounded-2xl p-8 border border-white/20 hover:bg-white/10 transition-all duration-300 hover:scale-105 hover:border-white/40">
                <h3 className="text-xl font-semibold text-white mb-3">
                  ML Predictions
                </h3>
                <p className="text-blue-100 text-sm leading-relaxed">
                  Research-grade RandomForest model predicting CO₂ emissions with high accuracy
                </p>
              </div>

              {/* Feature 2 */}
              <div className="group bg-white/5 rounded-2xl p-8 border border-white/20 hover:bg-white/10 transition-all duration-300 hover:scale-105 hover:border-white/40">
                <h3 className="text-xl font-semibold text-white mb-3">
                  ESG Scoring
                </h3>
                <p className="text-blue-100 text-sm leading-relaxed">
                  Deterministic environmental scoring with actionable risk flags and recommendations
                </p>
              </div>

              {/* Feature 3 */}
              <div className="group bg-white/5 rounded-2xl p-8 border border-white/20 hover:bg-white/10 transition-all duration-300 hover:scale-105 hover:border-white/40">
                <h3 className="text-xl font-semibold text-white mb-3">
                  Real-time Analysis
                </h3>
                <p className="text-blue-100 text-sm leading-relaxed">
                  Instant vessel analysis combining operational metrics with environmental impact
                </p>
              </div>
            </div>

            {/* CTA Button */}
            <div className="pt-8">
              <button
                onClick={() => navigate('/analyze')}
                className="group px-10 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-xl font-bold text-lg hover:from-cyan-400 hover:to-blue-400 transition-all duration-300 shadow-2xl hover:shadow-cyan-500/50 hover:scale-105"
              >
                <span className="flex items-center space-x-2">
                  <span>Start Analyzing</span>
                  <span className="group-hover:translate-x-1 transition-transform">→</span>
                </span>
              </button>
              <p className="mt-4 text-blue-200 text-sm">
                No sign-up required • Instant results • Powered by FastAPI & AWS
              </p>
            </div>
          </div>
        </main>
      </div>

      {/* Animated gradient background accent */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>
    </div>
  );
}

export default Landing;
