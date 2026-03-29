import './Gallery.css';
import logoUrl from './assets/logo.png';

const BeanPath =
  'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8 0-.42.04-.84.11-1.24.47-.07.95-.12 1.45-.12 4.41 0 8 3.59 8 8 0 .42-.04.84-.11 1.24-.47.07-.95.12-1.45.12zM19.89 10.76C19.42 10.83 18.94 10.88 18.44 10.88 14.03 10.88 10.44 7.29 10.44 2.88c0-.42.04-.84.11-1.24C15.01 1.7 18.67 5.14 19.89 10.76z';

const CoffeeBeansIcon = () => (
  <svg className="gallery-coffee-beans" width="46" height="46" viewBox="0 0 60 60" aria-hidden="true">
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

const ClapperIcon = () => (
  <svg viewBox="0 0 100 100" aria-hidden="true">
    <rect x="10" y="30" width="80" height="56" fill="none" stroke="#ffffff" strokeWidth="3" />
    <rect x="10" y="14" width="80" height="16" fill="none" stroke="#ffffff" strokeWidth="3" />
    <line x1="20" y1="14" x2="26" y2="30" stroke="#ffffff" strokeWidth="3" />
    <line x1="36" y1="14" x2="42" y2="30" stroke="#ffffff" strokeWidth="3" />
    <line x1="52" y1="14" x2="58" y2="30" stroke="#ffffff" strokeWidth="3" />
    <line x1="68" y1="14" x2="74" y2="30" stroke="#ffffff" strokeWidth="3" />
    <polygon points="40,44 66,58 40,72" fill="#ffffff" />
  </svg>
);

const Gallery = ({ onBack }) => {
  const projects = [
    { name: 'HAPPIER', files: '32 Audio Files , 32 Video File' },
    { name: 'ALONE', files: '32 Audio Files , 32 Video File' }
  ];

  return (
    <section className="gallery-page" aria-label="Gallery page">
      <div className="gallery-shell">
        <header className="gallery-topbar">
          <img src={logoUrl} alt="OASIS" className="gallery-logo" />
          <h1>MY LIBRARY</h1>
          <button type="button" className="gallery-back-btn" onClick={onBack} aria-label="Back to dashboard">
            <CoffeeBeansIcon />
          </button>
        </header>

        <div className="gallery-layout">
          <section className="gallery-left">
            <div className="turntable-card">
              <div className="turntable-deck">
                <div className="turntable-vinyl" />
                <div className="turntable-arm" />
                <div className="turntable-knobs">
                  <span />
                  <span />
                </div>
              </div>
              <h2>Happier</h2>
              <div className="playback-controls" aria-hidden="true">
                <span>♡</span>
                <span>◀◀</span>
                <span className="play-btn">▶</span>
                <span>▶▶</span>
                <span>⊕</span>
              </div>
            </div>
          </section>

          <section className="gallery-right">
            <div className="gallery-top-panels">
              <div className="clappers-panel">
                {Array.from({ length: 6 }).map((_, index) => (
                  <div key={`clapper-${index}`} className="clapper-item">
                    <ClapperIcon />
                  </div>
                ))}
              </div>

              <div className="albums-panel">
                {Array.from({ length: 4 }).map((_, index) => (
                  <div key={`album-${index}`} className="album-item">
                    <div className={`album-cover album-cover-${index % 2}`} />
                    <div className="album-record" />
                  </div>
                ))}
              </div>
            </div>

            <div className="recent-title">Recent Projects Files</div>

            <div className="projects-panel">
              {projects.map((project, index) => (
                <div key={project.name} className="project-row">
                  <div className={`project-thumb project-thumb-${index}`}>
                    {index === 0 ? (
                      <svg viewBox="0 0 64 64" className="project-thumb-icon" aria-hidden="true">
                        <circle cx="21" cy="26" r="9" fill="none" stroke="#f2e4de" strokeWidth="4" />
                        <circle cx="43" cy="26" r="9" fill="none" stroke="#f2e4de" strokeWidth="4" />
                        <path d="M30 26h4" stroke="#f2e4de" strokeWidth="4" strokeLinecap="round" />
                        <path d="M18 43c3 5 8 7 14 7s11-2 14-7" stroke="#f2e4de" strokeWidth="3" strokeLinecap="round" fill="none" />
                      </svg>
                    ) : (
                      <div className="project-thumb-orb" aria-hidden="true" />
                    )}
                  </div>
                  <div className="project-meta">
                    <h3>{project.name}</h3>
                    <p>{project.files}</p>
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

export default Gallery;
