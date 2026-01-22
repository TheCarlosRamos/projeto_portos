import React, { useState, useEffect } from 'react';
import { metasApi, processosApi, Meta, Processo } from '../services/api';
import './Metas.css';

const Metas: React.FC = () => {
  const [metas, setMetas] = useState<Meta[]>([]);
  const [processos, setProcessos] = useState<Processo[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<Partial<Meta>>({
    processo_id: undefined,
    ano: new Date().getFullYear(),
  });
  const [filtroAno, setFiltroAno] = useState<number | undefined>();
  const [filtroProcesso, setFiltroProcesso] = useState<number | undefined>();

  useEffect(() => {
    carregarDados();
  }, [filtroAno, filtroProcesso]);

  const carregarDados = async () => {
    try {
      setLoading(true);
      const [metasRes, processosRes] = await Promise.all([
        metasApi.listar({
          ano: filtroAno,
          processo_id: filtroProcesso,
        }),
        processosApi.listar({ limit: 1000 }),
      ]);
      setMetas(metasRes.data);
      setProcessos(processosRes.data);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      alert('Erro ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (formData.id) {
        await metasApi.atualizar(formData.id, formData);
      } else {
        await metasApi.criar(formData as Meta);
      }
      setShowForm(false);
      setFormData({
        processo_id: undefined,
        ano: new Date().getFullYear(),
      });
      carregarDados();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao salvar meta');
    }
  };

  const handleEdit = (meta: Meta) => {
    setFormData(meta);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Tem certeza que deseja excluir esta meta?')) {
      return;
    }
    try {
      await metasApi.deletar(id);
      carregarDados();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao excluir meta');
    }
  };

  if (loading) {
    return <div className="loading">Carregando...</div>;
  }

  return (
    <div className="metas">
      <div className="page-header">
        <h1>Metas</h1>
        <button className="btn-primary" onClick={() => {
          setFormData({
            processo_id: undefined,
            ano: new Date().getFullYear(),
          });
          setShowForm(true);
        }}>
          + Nova Meta
        </button>
      </div>

      <div className="filtros">
        <input
          type="number"
          placeholder="Filtrar por ano..."
          value={filtroAno || ''}
          onChange={(e) => setFiltroAno(e.target.value ? Number(e.target.value) : undefined)}
          className="input"
          min="2020"
          max="2100"
        />
        <select
          value={filtroProcesso || ''}
          onChange={(e) => setFiltroProcesso(e.target.value ? Number(e.target.value) : undefined)}
          className="select"
        >
          <option value="">Todos os processos</option>
          {processos.map((proc) => (
            <option key={proc.id} value={proc.id}>
              {proc.numero_processo}
            </option>
          ))}
        </select>
      </div>

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{formData.id ? 'Editar' : 'Nova'} Meta</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Processo *</label>
                <select
                  required
                  value={formData.processo_id || ''}
                  onChange={(e) => setFormData({ ...formData, processo_id: Number(e.target.value) })}
                  className="select"
                >
                  <option value="">Selecione...</option>
                  {processos.map((proc) => (
                    <option key={proc.id} value={proc.id}>
                      {proc.numero_processo}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Ano *</label>
                <input
                  type="number"
                  required
                  min="2020"
                  max="2100"
                  value={formData.ano}
                  onChange={(e) => setFormData({ ...formData, ano: Number(e.target.value) })}
                  className="input"
                />
              </div>
              <div className="form-actions">
                <button type="submit" className="btn-primary">Salvar</button>
                <button type="button" className="btn-secondary" onClick={() => setShowForm(false)}>
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th>Processo</th>
              <th>Ano</th>
              <th>Indicadores</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {metas.length === 0 ? (
              <tr>
                <td colSpan={4} className="empty-state">
                  Nenhuma meta encontrada
                </td>
              </tr>
            ) : (
              metas.map((meta) => (
                <tr key={meta.id}>
                  <td>
                    {processos.find((p) => p.id === meta.processo_id)?.numero_processo || '-'}
                  </td>
                  <td>{meta.ano}</td>
                  <td>{meta.indicadores?.length || 0}</td>
                  <td>
                    <button
                      className="btn-edit"
                      onClick={() => handleEdit(meta)}
                    >
                      ✏️
                    </button>
                    <button
                      className="btn-delete"
                      onClick={() => handleDelete(meta.id)}
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Metas;
