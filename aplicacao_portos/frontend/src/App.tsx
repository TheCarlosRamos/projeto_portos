import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Processos from './pages/Processos';
import Metas from './pages/Metas';
import Indicadores from './pages/Indicadores';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <main className="container">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/processos" element={<Processos />} />
            <Route path="/metas" element={<Metas />} />
            <Route path="/indicadores" element={<Indicadores />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
