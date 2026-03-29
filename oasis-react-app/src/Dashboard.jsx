import React, { useState, useEffect, useRef } from 'react';
import './Dashboard.css';
import logoUrl from './assets/logo.png';
import NavigationMenu from './NavigationMenu';

const BeanPath = "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8 0-.42.04-.84.11-1.24.47-.07.95-.12 1.45-.12 4.41 0 8 3.59 8 8 0 .42-.04.84-.11 1.24-.47.07-.95.12-1.45.12zM19.89 10.76C19.42 10.83 18.94 10.88 18.44 10.88 14.03 10.88 10.44 7.29 10.44 2.88c0-.42.04-.84.11-1.24C15.01 1.7 18.67 5.14 19.89 10.76z";

const ThreeCoffeeBeansMenu = () => (
  <svg className="coffee-beans-menu" width="60" height="60" viewBox="0 0 60 60">
    <g transform="translate(6, 6) rotate(-15 12 12) scale(1.15)">
      <path d={BeanPath} fill="#fffdf9" stroke="#4f1220" strokeWidth="1.7" />
    </g>
    <g transform="translate(14, 28) rotate(20 12 12) scale(1.15)">
      <path d={BeanPath} fill="#fffdf9" stroke="#4f1220" strokeWidth="1.7" />
    </g>
    <g transform="translate(30, 16) rotate(60 12 12) scale(1.25)">
      <path d={BeanPath} fill="#fffdf9" stroke="#4f1220" strokeWidth="1.7" />
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

const Dashboard = ({ onNavigateConnections, onNavigateGallery, onNavigateSettings }) => {
  const [isNavOpen, setIsNavOpen] = useState(false);
  const dashboardContainerRef = useRef(null);
  const weeklyProgress = [42, 56, 49, 64, 72, 68, 81];
  const progressCells = Array.from({ length: 120 }, (_, index) => {
    if (index % 37 === 0 || index % 41 === 0) return 'cell-hot';
    if (index % 9 === 0 || index % 13 === 0) return 'cell-mid';
    if (index % 5 === 0) return 'cell-low';
    return 'cell-empty';
  });

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setIsNavOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleNavigateHome = () => {
    setIsNavOpen(false);
    dashboardContainerRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleNavigateConnections = () => {
    setIsNavOpen(false);
    onNavigateConnections?.();
  };

  const handleNavigateGallery = () => {
    setIsNavOpen(false);
    onNavigateGallery?.();
  };

  const handleNavigateSettings = () => {
    setIsNavOpen(false);
    onNavigateSettings?.();
  };

  return (
    <div
      className={`dashboard-container${isNavOpen ? ' nav-open' : ''}`}
      ref={dashboardContainerRef}
    >
      <NavigationMenu
        isOpen={isNavOpen}
        onClose={() => setIsNavOpen(false)}
        onNavigateHome={handleNavigateHome}
        onNavigateConnections={handleNavigateConnections}
        onNavigateGallery={handleNavigateGallery}
        onNavigateSettings={handleNavigateSettings}
      />

      <header className="dash-header">
        <div className="dash-logo-container">
          <img src={logoUrl} alt="OASIS" className="dash-logo" />
        </div>
        <div className="dash-actions" onClick={() => setIsNavOpen(true)}>
          <ThreeCoffeeBeansMenu />
        </div>
      </header>

      <div className="dash-scroll-area">
        <section className="dash-section dash-section-home">
          <main className="dash-main">
            <h1 className="welcome-text">WELCOME USER</h1>

            <div className="cards-grid">
              <div className="grid-card add-card">
                <PlusIcon />
              </div>

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
        </section>

        <section className="dash-section dash-section-progress">
          <main className="dash-progress-main">
            <h2 className="progress-title">your progress</h2>

            <div className="progress-card">
              <div className="progress-visuals">
                <div className="progress-grid" aria-label="Progress heatmap">
                  {progressCells.map((cellClass, index) => (
                    <span key={index} className={`progress-cell ${cellClass}`} />
                  ))}
                </div>

                <aside className="progress-graph" aria-label="Weekly progress graph">
                  <span className="graph-caption">weekly</span>
                  <div className="graph-bars">
                    {weeklyProgress.map((value, index) => (
                      <span
                        key={index}
                        className={value >= 70 ? 'graph-bar graph-bar-hot' : 'graph-bar'}
                        style={{ height: `${value}%` }}
                      />
                    ))}
                  </div>
                </aside>
              </div>
            </div>

            <div className="dash-legal-links">
              <a href="#">Terms</a>
              <a href="#">Privacy</a>
              <a href="#">Security</a>
              <a href="#">Status</a>
              <a href="#">Community</a>
              <a href="#">Docs</a>
              <a href="#">Contact</a>
              <a href="#">Manage cookies</a>
            </div>
          </main>
        </section>
      </div>

      <footer className="dash-footer">
        <button className="user-profile-btn">
          <UserIcon />
        </button>
      </footer>
    </div>
  );
};

export default Dashboard;
