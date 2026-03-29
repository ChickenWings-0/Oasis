import React, { useState } from 'react';
import './App.css';
import Pattern from './Pattern';
import Landing from './Landing';
import Dashboard from './Dashboard';
import Connections from './Connections';
import Gallery from './Gallery';
import Settings from './Settings';

function App() {
  const [currentPage, setCurrentPage] = useState('landing');

  return (
    <div className="App">
      <Pattern />
      {currentPage === 'landing' ? (
        <Landing onComplete={() => setCurrentPage('dashboard')} />
      ) : currentPage === 'connections' ? (
        <Connections onBack={() => setCurrentPage('dashboard')} />
      ) : currentPage === 'gallery' ? (
        <Gallery onBack={() => setCurrentPage('dashboard')} />
      ) : currentPage === 'settings' ? (
        <Settings onBack={() => setCurrentPage('dashboard')} />
      ) : (
        <Dashboard
          onNavigateConnections={() => setCurrentPage('connections')}
          onNavigateGallery={() => setCurrentPage('gallery')}
          onNavigateSettings={() => setCurrentPage('settings')}
        />
      )}
    </div>
  )
}

export default App;
