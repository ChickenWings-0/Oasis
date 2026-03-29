import React from 'react';
import './Connections.css';
import logoUrl from './assets/logo.png';

const BeanPath = "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8 0-.42.04-.84.11-1.24.47-.07.95-.12 1.45-.12 4.41 0 8 3.59 8 8 0 .42-.04.84-.11 1.24-.47.07-.95.12-1.45.12zM19.89 10.76C19.42 10.83 18.94 10.88 18.44 10.88 14.03 10.88 10.44 7.29 10.44 2.88c0-.42.04-.84.11-1.24C15.01 1.7 18.67 5.14 19.89 10.76z";

const CoffeeBeansIcon = () => (
  <svg className="connections-coffee-beans" width="46" height="46" viewBox="0 0 60 60" aria-hidden="true">
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

const Connections = ({ onBack }) => {
  const artists = [
    { name: 'KIRA', role: 'MUSICIAN', tone: 'tone-cyan' },
    { name: 'KARL', role: 'MUSICIAN', tone: 'tone-stone' },
    { name: 'MARK', role: 'MUSICIAN', tone: 'tone-ink' },
    { name: 'ZENA', role: 'MUSICIAN', tone: 'tone-violet' }
  ];

  const topNetwork = [
    { name: 'ASTAN', role: 'MUSICIAN', mood: 'mood-soft' },
    { name: 'KIRJ', role: 'MUSICIAN', mood: 'mood-sharp' }
  ];

  return (
    <section className="connections-page" aria-label="Connections page">
      <div className="connections-shell">
        <header className="connections-topbar">
          <img src={logoUrl} alt="OASIS" className="connections-logo" />
          <h1>MY NETWORK</h1>
          <button type="button" className="connections-back-btn" onClick={onBack} aria-label="Back to dashboard">
            <CoffeeBeansIcon />
          </button>
        </header>

        <div className="connections-columns">
          <aside className="connections-left panel-shell">
            <div className="search-pill" role="search">
              <span>Search artist</span>
              <span className="search-icon" aria-hidden="true" />
            </div>

            <div className="artist-list">
              {artists.map((item) => (
                <article key={item.name} className="artist-item">
                  <span className={`artist-avatar ${item.tone}`} aria-hidden="true" />
                  <div>
                    <h2>{item.name}</h2>
                    <p>{item.role}</p>
                  </div>
                </article>
              ))}
            </div>
          </aside>

          <section className="connections-center">
            <article className="profile-card panel-shell">
              <div className="profile-copy">
                <h2>SHAUN</h2>
                <p>MUSICIAN</p>
                <div className="profile-stats">
                  <span>FOLLOWERS</span>
                  <strong>789</strong>
                  <span>FOLLOWING</span>
                  <strong>789</strong>
                </div>
              </div>

              <div className="profile-portrait" aria-hidden="true" />
            </article>

            <article className="top-network panel-shell">
              <h3>TOP NETWORK</h3>
              <div className="network-list">
                {topNetwork.map((item) => (
                  <div key={item.name} className="network-item">
                    <span className={`network-avatar ${item.mood}`} aria-hidden="true" />
                    <div>
                      <h4>{item.name}</h4>
                      <p>{item.role}</p>
                    </div>
                  </div>
                ))}
              </div>
            </article>
          </section>

          <aside className="connections-right panel-shell">
            <h3>TOP ALBUM</h3>
            <div className="album-vinyl" aria-hidden="true">
              <span className="vinyl-core" />
            </div>

            <div className="album-wave" aria-hidden="true">
              {Array.from({ length: 24 }).map((_, index) => (
                <span key={index} style={{ height: `${8 + ((index * 7) % 18)}px` }} />
              ))}
            </div>

            <div className="album-controls" aria-hidden="true">
              <span className="control-arrow">&lt;&lt;</span>
              <span className="control-play">||</span>
              <span className="control-arrow">&gt;&gt;</span>
            </div>

            <div className="album-stats">
              <div>
                <span>TIMES PLAYED</span>
                <strong>789</strong>
              </div>
              <div>
                <span>TIMES USED</span>
                <strong>789</strong>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </section>
  );
};

export default Connections;
