import './Settings.css';
import logoUrl from './assets/logo.png';

const BeanPath =
  'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8 0-.42.04-.84.11-1.24.47-.07.95-.12 1.45-.12 4.41 0 8 3.59 8 8 0 .42-.04.84-.11 1.24-.47.07-.95.12-1.45.12zM19.89 10.76C19.42 10.83 18.94 10.88 18.44 10.88 14.03 10.88 10.44 7.29 10.44 2.88c0-.42.04-.84.11-1.24C15.01 1.7 18.67 5.14 19.89 10.76z';

const CoffeeBeansIcon = () => (
  <svg className="settings-coffee-beans" width="46" height="46" viewBox="0 0 60 60" aria-hidden="true">
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

const Settings = ({ onBack }) => {
  return (
    <section className="settings-page" aria-label="Settings page">
      <div className="settings-shell">
        <header className="settings-topbar">
          <img src={logoUrl} alt="OASIS" className="settings-logo" />
          <button type="button" className="settings-back-btn" onClick={onBack} aria-label="Back to dashboard">
            <CoffeeBeansIcon />
          </button>
        </header>

        <div className="settings-layout">
          <aside className="settings-profile-card">
            <div className="settings-avatar" aria-hidden="true">
              <span className="eye eye-left" />
              <span className="eye eye-right" />
              <span className="smile" />
            </div>
            <h2>KIRA</h2>
            <p>MUSICIAN</p>
          </aside>

          <div className="settings-divider" aria-hidden="true">
            {Array.from({ length: 8 }).map((_, index) => (
              <span key={`dot-${index}`} className="settings-dot" />
            ))}
          </div>

          <section className="settings-main-panel" aria-label="Settings content area" />
        </div>

        <footer className="settings-footer-note">Turn imagination into weaponized reality</footer>
      </div>
    </section>
  );
};

export default Settings;
