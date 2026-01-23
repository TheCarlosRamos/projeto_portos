import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

const Navbar: React.FC = () => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          🚢 Sistema Portuário
        </Link>
        <div className="navbar-menu">
          <Link to="/" className="navbar-link">Início</Link>
          <Link to="/portos" className="navbar-link">🚢 Portos</Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
