import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

const Home: React.FC = () => {
  return (
    <div className="home">
      <div className="hero">
        <h1>Bem-vindo ao Sistema de Gestão de Processos e Metas</h1>
        <p className="subtitle">
          Sistema web para cadastro, gerenciamento, acompanhamento e análise de processos administrativos e metas físicas/financeiras.
        </p>
      </div>

      <div className="features">
        <div className="feature-card">
          <div className="feature-icon">📄</div>
          <h3>Processos</h3>
          <p>Gerencie processos administrativos de forma centralizada</p>
          <Link to="/processos" className="feature-link">Ver Processos →</Link>
        </div>

        <div className="feature-card">
          <div className="feature-icon">📅</div>
          <h3>Metas</h3>
          <p>Acompanhe metas por ano e processo</p>
          <Link to="/metas" className="feature-link">Ver Metas →</Link>
        </div>

        <div className="feature-card">
          <div className="feature-icon">📊</div>
          <h3>Indicadores</h3>
          <p>Monitore indicadores físicos e financeiros</p>
          <Link to="/indicadores" className="feature-link">Ver Indicadores →</Link>
        </div>
      </div>

      <div className="info-section">
        <h2>Funcionalidades</h2>
        <ul>
          <li>✅ Cadastro e edição de processos administrativos</li>
          <li>✅ Gerenciamento de metas por ano</li>
          <li>✅ Controle de indicadores físicos e financeiros</li>
          <li>✅ Filtros e buscas avançadas</li>
          <li>✅ Importação de dados via planilhas Excel</li>
          <li>✅ Dashboard analítico e relatórios</li>
        </ul>
      </div>
    </div>
  );
};

export default Home;
