import React, { useState } from 'react';
import './App.css';
import Pattern from './Pattern';
import Landing from './Landing';
import Dashboard from './Dashboard';

function App() {
  const [currentPage, setCurrentPage] = useState('landing');

  return (
    <div className="App">
      <Pattern />
      {currentPage === 'landing' ? (
        <Landing onComplete={() => setCurrentPage('dashboard')} />
      ) : (
        <Dashboard />
      )}
    </div>
  )
}

export default App;
