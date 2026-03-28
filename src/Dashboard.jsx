import React, { useState, useEffect } from 'react';
import './Dashboard.css';
import logoUrl from './assets/logo.png';
import NavigationMenu from './NavigationMenu';

const BeanPath = "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8 0-.42.04-.84.11-1.24.47-.07.95-.12 1.45-.12 4.41 0 8 3.59 8 8 0 .42-.04.84-.11 1.24-.47.07-.95.12-1.45.12zM19.89 10.76C19.42 10.83 18.94 10.88 18.44 10.88 14.03 10.88 10.44 7.29 10.44 2.88c0-.42.04-.84.11-1.24C15.01 1.7 18.67 5.14 19.89 10.76z";

const ThreeCoffeeBeansMenu = () => (
  <svg className="coffee-beans-menu" width="60" height="60" viewBox="0 0 60 60">
    <g transform="translate(6, 6) rotate(-15 12 12) scale(1.15)">
      <path d={BeanPath} fill="#59121e" stroke="#050002" strokeWidth="1.5" />
    </g>
    <g transform="translate(14, 28) rotate(20 12 12) scale(1.15)">
      <path d={BeanPath} fill="#59121e" stroke="#050002" strokeWidth="1.5" />
    </g>
    <g transform="translate(30, 16) rotate(60 12 12) scale(1.25)">
      <path d={BeanPath} fill="#59121e" stroke="#050002" strokeWidth="1.5" />
    </g>
  </svg>
);

const PlusIcon = () => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" strokeWidth="1.5"></circle>
    <line x1="12" y1="8" x2="12" y2="16"></line>
    <line x1="8" y1="12" x2="16" y2="12"></line>
  </svg>
);

const UserIcon = () => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" strokeWidth="1.5"></circle>
    <path d="M18 20a6 6 0 0 0-12 0"></path>
    <circle cx="12" cy="10" r="4"></circle>
  </svg>
);

const Dashboard = () => {
  const [isNavOpen, setIsNavOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e) => {
      // Toggle menu on Escape key press
      if (e.key === 'Escape') {
        setIsNavOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="dashboard-container">
      <NavigationMenu isOpen={isNavOpen} onClose={() => setIsNavOpen(false)} />
      
      {/* HEADER */}
      <header className="dash-header">
        <div className="dash-logo-container">
          <img src={logoUrl} alt="OASIS" className="dash-logo" />
        </div>
        <div className="dash-actions" onClick={() => setIsNavOpen(true)}>
          <ThreeCoffeeBeansMenu />
        </div>
      </header>

      {/* MAIN CONTENT */}
      <main className="dash-main">
        <h1 className="welcome-text">WELCOME USER</h1>
        
        <div className="cards-grid">
          {/* Add New Card */}
          <div className="grid-card add-card">
            <PlusIcon />
          </div>
          
          {/* Placeholder Gallery Cards */}
          {[...Array(6)].map((_, index) => (
            <div className="grid-card album-card" key={index}>
              <div className="album-placeholder-wrapper">
                <div className="album-art-placeholder">
                  <span className="album-title">PAIN</span>
                  <span className="album-artist">RYAN JONES</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* FOOTER */}
      <footer className="dash-footer">
        <button className="user-profile-btn">
          <UserIcon />
        </button>
      </footer>
    </div>
  );
};

export default Dashboard;
