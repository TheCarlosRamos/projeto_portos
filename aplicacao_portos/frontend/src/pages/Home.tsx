import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

const Home: React.FC = () => {
  return (
    <div className="home">
      <div className="hero">
        <h1>🚢 Sistema Portuário</h1>
        <p className="subtitle">
          Sistema completo para gestão de concessões portuárias, serviços e acompanhamentos.
        </p>
      </div>

      <div className="features">
        <div className="feature-card featured">
          <div className="feature-icon">🚢</div>
          <h3>Sistema Portuário</h3>
          <p>Gestão completa de concessões, serviços e acompanhamentos portuários</p>
          <Link to="/portos" className="feature-link">Acessar Sistema Portuário →</Link>
        </div>
      </div>

      <div className="info-section">
        <h2>Sistema Portuário - Funcionalidades</h2>
        <ul>
          <li> Cadastro de Concessões Portuárias</li>
          <li> Gestão de Serviços com % CAPEX</li>
          <li> Acompanhamento de Obras e Serviços</li>
          <li> Importação de Planilhas Excel</li>
          <li> Relatórios e Indicadores em Tempo Real</li>
          <li> Estrutura Baseada na Planilha Real</li>
        </ul>
        

      </div>
    </div>
  );
};

export default Home;
