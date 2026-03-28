import React, { useEffect } from 'react';
import './Landing.css';
import logoUrl from './assets/logo.png';

const Landing = ({ onComplete }) => {
  useEffect(() => {
    // Auto-switch to Dashboard after 4 seconds
    const timer = setTimeout(() => {
      onComplete();
    }, 4000);
    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <div className="landing-content">
      <img src={logoUrl} alt="OASIS" className="logo" />
      <p className="tagline">Turn imagination into weaponized reality.</p>
    </div>
  );
};

export default Landing;
