import React, { useState, useEffect } from 'react';
import { indicadoresApi, metasApi, Indicador, Meta } from '../services/api';
import './Indicadores.css';

const Indicadores: React.FC = () => {
  const [indicadores, setIndicadores] = useState<Indicador[]>([]);
  const [metas, setMetas] = useState<Meta[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<Partial<Indicador>>({
    meta_id: undefined,
    tipo_intervencao: '',
    financeiro_planejado: 0,
    financeiro_executado: 0,
    km_planejado: 0,
    km_executado: 0,
    extensao_km: 0,
  });
  const [filtroMeta, setFiltroMeta] = useState<number | undefined>();
  const [filtroTipo, setFiltroTipo] = useState('');

  useEffect(() => {
    carregarDados();
  }, [filtroMeta, filtroTipo]);

  const carregarDados = async () => {
    try {
      setLoading(true);
      const [indicadoresRes, metasRes] = await Promise.all([
        indicadoresApi.listar({
          meta_id: filtroMeta,
          tipo_intervencao: filtroTipo || undefined,
        }),
        metasApi.listar({ limit: 1000 }),
      ]);
      setIndicadores(indicadoresRes.data);
      setMetas(metasRes.data);
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
        await indicadoresApi.atualizar(formData.id, formData);
      } else {
        await indicadoresApi.criar(formData as Indicador);
      }
      setShowForm(false);
      setFormData({
        meta_id: undefined,
        tipo_intervencao: '',
        financeiro_planejado: 0,
        financeiro_executado: 0,
        km_planejado: 0,
        km_executado: 0,
        extensao_km: 0,
      });
      carregarDados();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao salvar indicador');
    }
  };

  const handleEdit = (indicador: Indicador) => {
    setFormData(indicador);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Tem certeza que deseja excluir este indicador?')) {
      return;
    }
    try {
      await indicadoresApi.deletar(id);
      carregarDados();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao excluir indicador');
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  if (loading) {
    return <div className="loading">Carregando...</div>;
  }

  return (
    <div className="indicadores">
      <div className="page-header">
        <h1>Indicadores</h1>
        <button className="btn-primary" onClick={() => {
          setFormData({
            meta_id: undefined,
            tipo_intervencao: '',
            financeiro_planejado: 0,
            financeiro_executado: 0,
            km_planejado: 0,
            km_executado: 0,
            extensao_km: 0,
          });
          setShowForm(true);
        }}>
          + Novo Indicador
        </button>
      </div>

      <div className="filtros">
        <input
          type="text"
          placeholder="Filtrar por tipo de intervenção..."
          value={filtroTipo}
          onChange={(e) => setFiltroTipo(e.target.value)}
          className="input"
        />
        <select
          value={filtroMeta || ''}
          onChange={(e) => setFiltroMeta(e.target.value ? Number(e.target.value) : undefined)}
          className="select"
        >
          <option value="">Todas as metas</option>
          {metas.map((meta) => (
            <option key={meta.id} value={meta.id}>
              Meta {meta.ano} (ID: {meta.id})
            </option>
          ))}
        </select>
      </div>

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal modal-large" onClick={(e) => e.stopPropagation()}>
            <h2>{formData.id ? 'Editar' : 'Novo'} Indicador</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Meta *</label>
                <select
                  required
                  value={formData.meta_id || ''}
                  onChange={(e) => setFormData({ ...formData, meta_id: Number(e.target.value) })}
                  className="select"
                >
                  <option value="">Selecione...</option>
                  {metas.map((meta) => (
                    <option key={meta.id} value={meta.id}>
                      Meta {meta.ano} (ID: {meta.id})
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Tipo de Intervenção *</label>
                <input
                  type="text"
                  required
                  value={formData.tipo_intervencao}
                  onChange={(e) => setFormData({ ...formData, tipo_intervencao: e.target.value })}
                  className="input"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>Financeiro Planejado (R$)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.financeiro_planejado}
                    onChange={(e) => setFormData({ ...formData, financeiro_planejado: Number(e.target.value) })}
                    className="input"
                  />
                </div>
                <div className="form-group">
                  <label>Financeiro Executado (R$)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.financeiro_executado}
                    onChange={(e) => setFormData({ ...formData, financeiro_executado: Number(e.target.value) })}
                    className="input"
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>KM Planejado</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.km_planejado}
                    onChange={(e) => setFormData({ ...formData, km_planejado: Number(e.target.value) })}
                    className="input"
                  />
                </div>
                <div className="form-group">
                  <label>KM Executado</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.km_executado}
                    onChange={(e) => setFormData({ ...formData, km_executado: Number(e.target.value) })}
                    className="input"
                  />
                </div>
                <div className="form-group">
                  <label>Extensão KM</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.extensao_km}
                    onChange={(e) => setFormData({ ...formData, extensao_km: Number(e.target.value) })}
                    className="input"
                  />
                </div>
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
              <th>Tipo Intervenção</th>
              <th>Financeiro Planejado</th>
              <th>Financeiro Executado</th>
              <th>KM Planejado</th>
              <th>KM Executado</th>
              <th>Extensão KM</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {indicadores.length === 0 ? (
              <tr>
                <td colSpan={7} className="empty-state">
                  Nenhum indicador encontrado
                </td>
              </tr>
            ) : (
              indicadores.map((indicador) => (
                <tr key={indicador.id}>
                  <td>{indicador.tipo_intervencao}</td>
                  <td>{formatCurrency(Number(indicador.financeiro_planejado))}</td>
                  <td>{formatCurrency(Number(indicador.financeiro_executado))}</td>
                  <td>{indicador.km_planejado}</td>
                  <td>{indicador.km_executado}</td>
                  <td>{indicador.extensao_km}</td>
                  <td>
                    <button
                      className="btn-edit"
                      onClick={() => handleEdit(indicador)}
                    >
                      ✏️
                    </button>
                    <button
                      className="btn-delete"
                      onClick={() => handleDelete(indicador.id)}
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

export default Indicadores;
