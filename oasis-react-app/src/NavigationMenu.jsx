import React from 'react';
import './NavigationMenu.css';
import logoUrl from './assets/logo.png';

// Custom detailed icons for the Nav overlay
const HomeIcon = () => (
  <svg viewBox="0 0 24 24" fill="#0b0204" xmlns="http://www.w3.org/2000/svg">
    <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" />
  </svg>
);

const RecordIcon = () => (
  <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="32" cy="32" r="28" fill="#111" stroke="#000" strokeWidth="2" />
    <circle cx="32" cy="32" r="22" stroke="#222" strokeWidth="1" />
    <circle cx="32" cy="32" r="16" stroke="#222" strokeWidth="1" />
    <circle cx="32" cy="32" r="10" fill="#d9531e" />
    <circle cx="32" cy="32" r="3" fill="#000" />
  </svg>
);

const CassetteIcon = () => (
  <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="8" y="16" width="48" height="32" rx="4" fill="#111" />
    <rect x="14" y="22" width="36" height="14" fill="#b08b68" />
    <circle cx="22" cy="29" r="4" fill="#000" />
    <circle cx="42" cy="29" r="4" fill="#000" />
    <path d="M20 42h24l2-6H18l2 6z" fill="#222" />
  </svg>
);

const NetworkIcon = () => (
  <svg viewBox="0 0 64 64" fill="none" stroke="#0b0204" strokeWidth="3" xmlns="http://www.w3.org/2000/svg">
    <circle cx="32" cy="26" r="6" />
    <path d="M22 42c0-6 5-10 10-10s10 4 10 10" />
    <circle cx="12" cy="18" r="3" />
    <circle cx="52" cy="18" r="3" />
    <circle cx="16" cy="48" r="3" />
    <circle cx="48" cy="48" r="3" />
    <path d="M26 26L14 19 M38 26l12-7 M24 38l-6 8 M40 38l6 8" />
  </svg>
);

const GalleryIcon = () => (
  <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="12" y="14" width="40" height="36" rx="2" fill="#b08b68" />
    <rect x="16" y="18" width="32" height="28" fill="#111" />
    <path d="M16 46l10-14 6 8 8-12 8 18H16z" fill="#fff" opacity="0.8" />
    <circle cx="26" cy="26" r="3" fill="#fff" />
  </svg>
);

const SettingsIcon = () => (
  <svg viewBox="0 0 24 24" fill="#0b0204" xmlns="http://www.w3.org/2000/svg">
    <path d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.06-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.73,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.06,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.43-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.49-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z" />
  </svg>
);

const UserIconOutline = () => (
  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="11"></circle>
    <path d="M18 19a6 6 0 0 0-12 0"></path>
    <circle cx="12" cy="9" r="4"></circle>
  </svg>
);

const NavigationMenu = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="nav-overlay" onClick={onClose}>
      <div className="nav-content" onClick={e => e.stopPropagation()}>
        <header className="nav-header">
          <div className="nav-logo-wrapper">
             <img src={logoUrl} alt="OASIS" className="nav-logo" />
          </div>
          <button className="nav-user-btn" onClick={onClose}>
             <UserIconOutline />
          </button>
        </header>
        
        <main className="nav-grid">
           <div className="nav-item"><HomeIcon /></div>
           <div className="nav-item"><RecordIcon /></div>
           <div className="nav-item"><CassetteIcon /></div>
           <div className="nav-item"><NetworkIcon /></div>
           <div className="nav-item"><GalleryIcon /></div>
           <div className="nav-item"><SettingsIcon /></div>
        </main>
      </div>
    </div>
  );
};

export default NavigationMenu;
