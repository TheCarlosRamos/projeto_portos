import React, { useState, useEffect } from 'react';
import { processosApi, situacoesApi, etlApi, Processo, Situacao } from '../services/api';
import './Processos.css';

const Processos: React.FC = () => {
  const [processos, setProcessos] = useState<Processo[]>([]);
  const [situacoes, setSituacoes] = useState<Situacao[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [importing, setImporting] = useState(false);
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

  const handleFileImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
      alert('Por favor, selecione um arquivo Excel (.xlsx ou .xls)');
      return;
    }

    setImporting(true);
    try {
      await etlApi.importarExcel(file);
      alert('Planilha importada com sucesso!');
      setShowImportModal(false);
      carregarDados();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao importar planilha');
    } finally {
      setImporting(false);
    }
  };

  if (loading) {
    return <div className="loading">Carregando...</div>;
  }

  return (
    <div className="processos">
      <div className="page-header">
        <h1>Processos</h1>
        <div className="header-buttons">
          <button className="btn-secondary" onClick={() => setShowImportModal(true)}>
            📊 Importar Excel
          </button>
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

      {showImportModal && (
        <div className="modal-overlay" onClick={() => setShowImportModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Importar Planilha Excel</h2>
            <div className="import-info">
              <p><strong>Formato esperado:</strong></p>
              <ul>
                <li>Arquivo Excel (.xlsx ou .xls)</li>
                <li>Abas com nomes contendo anos (ex: "2023", "Dados 2024")</li>
                <li>Colunas: "nº processo", "data do protocolo", "licença", "situação geral"</li>
                <li>Opcional: colunas de indicadores (financeiro, km, etc.)</li>
              </ul>
            </div>
            <div className="form-group">
              <label>Selecione o arquivo Excel:</label>
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleFileImport}
                disabled={importing}
                className="input"
              />
            </div>
            <div className="form-actions">
              <button 
                type="button" 
                className="btn-secondary" 
                onClick={() => setShowImportModal(false)}
                disabled={importing}
              >
                Cancelar
              </button>
            </div>
            {importing && (
              <div className="importing-message">
                Processando planilha... Isso pode levar alguns minutos.
              </div>
            )}
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
