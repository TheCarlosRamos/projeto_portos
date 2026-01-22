import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

const Navbar: React.FC = () => {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          📊 Gestão de Processos e Metas
        </Link>
        <div className="navbar-menu">
          <Link to="/" className="navbar-link">Início</Link>
          <Link to="/processos" className="navbar-link">Processos</Link>
          <Link to="/metas" className="navbar-link">Metas</Link>
          <Link to="/indicadores" className="navbar-link">Indicadores</Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
