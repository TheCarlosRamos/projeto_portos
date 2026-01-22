import React, { useState, useEffect } from 'react';
import { processosApi, situacoesApi, Processo, Situacao } from '../services/api';
import './Processos.css';

const Processos: React.FC = () => {
  const [processos, setProcessos] = useState<Processo[]>([]);
  const [situacoes, setSituacoes] = useState<Situacao[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<Partial<Processo>>({
    numero_processo: '',
    data_protocolo: '',
    licenca: '',
    situacao_geral_id: undefined,
  });
  const [filtroNumero, setFiltroNumero] = useState('');
  const [filtroSituacao, setFiltroSituacao] = useState<number | undefined>();

  useEffect(() => {
    carregarDados();
  }, [filtroNumero, filtroSituacao]);

  const carregarDados = async () => {
    try {
      setLoading(true);
      const [processosRes, situacoesRes] = await Promise.all([
        processosApi.listar({
          numero_processo: filtroNumero || undefined,
          situacao_id: filtroSituacao,
        }),
        situacoesApi.listar(),
      ]);
      setProcessos(processosRes.data);
      setSituacoes(situacoesRes.data);
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
        await processosApi.atualizar(formData.id, formData);
      } else {
        await processosApi.criar(formData);
      }
      setShowForm(false);
      setFormData({
        numero_processo: '',
        data_protocolo: '',
        licenca: '',
        situacao_geral_id: undefined,
      });
      carregarDados();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao salvar processo');
    }
  };

  const handleEdit = (processo: Processo) => {
    setFormData(processo);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Tem certeza que deseja excluir este processo?')) {
      return;
    }
    try {
      await processosApi.deletar(id);
      carregarDados();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao excluir processo');
    }
  };

  if (loading) {
    return <div className="loading">Carregando...</div>;
  }

  return (
    <div className="processos">
      <div className="page-header">
        <h1>Processos</h1>
        <button className="btn-primary" onClick={() => {
          setFormData({
            numero_processo: '',
            data_protocolo: '',
            licenca: '',
            situacao_geral_id: undefined,
          });
          setShowForm(true);
        }}>
          + Novo Processo
        </button>
      </div>

      <div className="filtros">
        <input
          type="text"
          placeholder="Filtrar por número do processo..."
          value={filtroNumero}
          onChange={(e) => setFiltroNumero(e.target.value)}
          className="input"
        />
        <select
          value={filtroSituacao || ''}
          onChange={(e) => setFiltroSituacao(e.target.value ? Number(e.target.value) : undefined)}
          className="select"
        >
          <option value="">Todas as situações</option>
          {situacoes.map((sit) => (
            <option key={sit.id} value={sit.id}>
              {sit.nome}
            </option>
          ))}
        </select>
      </div>

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{formData.id ? 'Editar' : 'Novo'} Processo</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Número do Processo *</label>
                <input
                  type="text"
                  required
                  value={formData.numero_processo}
                  onChange={(e) => setFormData({ ...formData, numero_processo: e.target.value })}
                  className="input"
                />
              </div>
              <div className="form-group">
                <label>Data do Protocolo</label>
                <input
                  type="date"
                  value={formData.data_protocolo}
                  onChange={(e) => setFormData({ ...formData, data_protocolo: e.target.value })}
                  className="input"
                />
              </div>
              <div className="form-group">
                <label>Licença</label>
                <input
                  type="text"
                  value={formData.licenca}
                  onChange={(e) => setFormData({ ...formData, licenca: e.target.value })}
                  className="input"
                />
              </div>
              <div className="form-group">
                <label>Situação</label>
                <select
                  value={formData.situacao_geral_id || ''}
                  onChange={(e) => setFormData({ ...formData, situacao_geral_id: e.target.value ? Number(e.target.value) : undefined })}
                  className="select"
                >
                  <option value="">Selecione...</option>
                  {situacoes.map((sit) => (
                    <option key={sit.id} value={sit.id}>
                      {sit.nome}
                    </option>
                  ))}
                </select>
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
              <th>Número</th>
              <th>Data Protocolo</th>
              <th>Licença</th>
              <th>Situação</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {processos.length === 0 ? (
              <tr>
                <td colSpan={5} className="empty-state">
                  Nenhum processo encontrado
                </td>
              </tr>
            ) : (
              processos.map((processo) => (
                <tr key={processo.id}>
                  <td>{processo.numero_processo}</td>
                  <td>{processo.data_protocolo || '-'}</td>
                  <td>{processo.licenca || '-'}</td>
                  <td>{processo.situacao?.nome || '-'}</td>
                  <td>
                    <button
                      className="btn-edit"
                      onClick={() => handleEdit(processo)}
                    >
                      ✏️
                    </button>
                    <button
                      className="btn-delete"
                      onClick={() => handleDelete(processo.id)}
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

export default Processos;
