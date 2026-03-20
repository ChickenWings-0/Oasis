"use client";

import React from 'react';

const Navbar = () => {
  // Simple logout function
  const handleLogout = () => {
    console.log("User logged out");
    window.location.href = "/";
  };

  return (
    <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Logo */}
          <div className="flex items-center">
            <a href="/" className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              Oasis
            </a>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
            <a href="/dashboard" className="text-gray-600 hover:text-indigo-600 transition-colors font-medium">Dashboard</a>
            <a href="/oasis-studio" className="text-gray-600 hover:text-indigo-600 transition-colors font-medium">Oasis Studio</a>
            <a href="/video-generator" className="text-gray-600 hover:text-indigo-600 transition-colors font-medium">Video Generator</a>
            <a href="/video-editor" className="text-gray-600 hover:text-indigo-600 transition-colors font-medium">Video Editor</a>
            <a href="#" className="text-gray-600 hover:text-indigo-600 transition-colors font-medium">Content Generator</a>
            <a href="#" className="text-gray-600 hover:text-indigo-600 transition-colors font-medium">History</a>
          </div>

          {/* Logout Button */}
          <div className="flex items-center">
            <button 
              onClick={handleLogout}
              className="bg-red-50 text-red-600 px-4 py-2 rounded-lg font-medium hover:bg-red-100 transition-all duration-200"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
