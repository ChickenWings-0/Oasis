import React from 'react';
import './Library.css';
import logoUrl from './assets/logo.png';

const BeanPath = "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8 0-.42.04-.84.11-1.24.47-.07.95-.12 1.45-.12 4.41 0 8 3.59 8 8 0 .42-.04.84-.11 1.24-.47.07-.95.12-1.45.12zM19.89 10.76C19.42 10.83 18.94 10.88 18.44 10.88 14.03 10.88 10.44 7.29 10.44 2.88c0-.42.04-.84.11-1.24C15.01 1.7 18.67 5.14 19.89 10.76z";

const CoffeeBeansIcon = () => (
  <svg className="library-coffee-beans" width="46" height="46" viewBox="0 0 60 60" aria-hidden="true">
    <g transform="translate(6, 6) rotate(-15 12 12) scale(1.1)">
      <path d={BeanPath} fill="#fffdf9" stroke="#4f1220" strokeWidth="1.7" />
    </g>
    <g transform="translate(14, 28) rotate(20 12 12) scale(1.1)">
      <path d={BeanPath} fill="#fffdf9" stroke="#4f1220" strokeWidth="1.7" />
    </g>
    <g transform="translate(30, 16) rotate(60 12 12) scale(1.2)">
      <path d={BeanPath} fill="#fffdf9" stroke="#4f1220" strokeWidth="1.7" />
    </g>
  </svg>
);

const Library = ({ onBack }) => {
  const projects = [
    { name: 'HAPPIER', audioFiles: 32, videoFiles: 32 },
    { name: 'ALONE', audioFiles: 32, videoFiles: 32 }
  ];

  return (
    <section className="library-page" aria-label="Library page">
      <div className="library-shell">
        <header className="library-topbar">
          <img src={logoUrl} alt="OASIS" className="library-logo" />
          <h1>MY LIBRARY</h1>
          <button type="button" className="library-back-btn" onClick={onBack} aria-label="Back to dashboard">
            <CoffeeBeansIcon />
          </button>
        </header>

        <div className="library-layout">
          {/* LEFT: TURNTABLE SECTION */}
          <section className="library-left">
            <div className="turntable-card">
              <div className="turntable-visual">
                <div className="vinyl-disk">
                  <div className="vinyl-rings" />
                </div>
                <div className="turntable-arm" />
              </div>
              <h2>HAPPIER</h2>
              <div className="playback-controls">
                <button className="control-heart" aria-label="Like" />
                <button className="control-prev" aria-label="Previous" />
                <button className="control-play" aria-label="Play" />
                <button className="control-next" aria-label="Next" />
                <button className="control-add" aria-label="Add" />
              </div>
            </div>
          </section>

          {/* CENTER: FILMS & ALBUMS */}
          <section className="library-center">
            <div className="films-grid">
              {Array.from({ length: 6 }).map((_, idx) => (
                <div key={idx} className="film-clapper">
                  <svg viewBox="0 0 100 100">
                    <rect x="10" y="10" width="80" height="80" rx="4" fill="none" stroke="white" strokeWidth="2" />
                    <g fill="white">
                      <rect x="15" y="15" width="16" height="12" />
                      <rect x="35" y="15" width="16" height="12" />
                      <rect x="55" y="15" width="16" height="12" />
                      <polygon points="30,50 50,35 50,65" />
                    </g>
                  </svg>
                </div>
              ))}
            </div>

            <div className="albums-grid">
              {Array.from({ length: 4 }).map((_, idx) => (
                <div key={idx} className="album-card">
                  <div className="album-vinyl-small">
                    <div className={`album-cover album-cover-${idx % 2}`} />
                  </div>
                </div>
              ))}
            </div>

            <div className="recent-projects-label">Recent Projects Files</div>

            <div className="projects-list">
              {projects.map((project) => (
                <div key={project.name} className="project-item">
                  <div className="project-icon" />
                  <div>
                    <h3>{project.name}</h3>
                    <p>{project.audioFiles} Audio Files , {project.videoFiles} Video File</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>
    </section>
  );
};

export default Library;
