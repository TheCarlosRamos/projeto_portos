import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { portosApi } from '../services/api';
import './Portos.css';

interface Concessao {
  id: number;
  zona_portuaria: { nome: string; uf: string };
  objeto_concessao: string;
  tipo: string;
  capex_total: number;
  data_assinatura: string;
  descricao: string;
  coord_e: number;
  coord_s: number;
  fuso: number;
  created_at: string;
  updated_at: string;
}

interface Servico {
  id: number;
  concessao: Concessao;
  tipo_servico: { nome: string };
  fase: string;
  nome: string;
  descricao: string;
  prazo_inicio_anos: number;
  data_inicio: string;
  prazo_final_anos: number;
  data_final: string;
  fonte_prazo: string;
  percentual_capex: number;
  capex_servico: number;
  fonte_percentual: string;
  created_at: string;
  updated_at: string;
}

interface Acompanhamento {
  id: number;
  servico: Servico;
  percentual_executado: number;
  capex_reajustado: number;
  valor_executado: number;
  data_atualizacao: string;
  responsavel: string;
  cargo: string;
  setor: string;
  created_at: string;
  riscos: Array<{ tipo: string; descricao: string }>;
}

const Portos: React.FC = () => {
  const [abaAtiva, setAbaAtiva] = useState<'concessoes' | 'servicos' | 'acompanhamentos'>('concessoes');
  const [concessoes, setConcessoes] = useState<Concessao[]>([]);
  const [servicos, setServicos] = useState<Servico[]>([]);
  const [acompanhamentos, setAcompanhamentos] = useState<Acompanhamento[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  
  // Estados para formulários
  const [showConcessaoForm, setShowConcessaoForm] = useState(false);
  const [showServicoForm, setShowServicoForm] = useState(false);
  const [showAcompanhamentoForm, setShowAcompanhamentoForm] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [importing, setImporting] = useState(false);

  useEffect(() => {
    carregarDados();
  }, [abaAtiva]); // eslint-disable-line react-hooks/exhaustive-deps

  const carregarDados = async () => {
    setCarregando(true);
    setErro(null);
    
    try {
      console.log('Carregando dados para aba:', abaAtiva);
      switch (abaAtiva) {
        case 'concessoes':
          await carregarConcessoes();
          break;
        case 'servicos':
          await carregarServicos();
          break;
        case 'acompanhamentos':
          await carregarAcompanhamentos();
          break;
      }
      console.log('Dados carregados:', { concessoes, servicos, acompanhamentos });
    } catch (error) {
      setErro('Erro ao carregar dados');
      console.error(error);
    } finally {
      setCarregando(false);
    }
  };

  const carregarConcessoes = async () => {
    console.log('Carregando concessões...');
    const response = await portosApi.listarConcessoes();
    console.log('Concessões recebidas:', response.data);
    setConcessoes(response.data);
  };

  const carregarServicos = async () => {
    console.log('Carregando serviços...');
    const response = await portosApi.listarServicos();
    console.log('Serviços recebidos:', response.data);
    setServicos(response.data);
  };

  const carregarAcompanhamentos = async () => {
    console.log('Carregando acompanhamentos...');
    const response = await portosApi.listarAcompanhamentos();
    console.log('Acompanhamentos recebidos:', response.data);
    setAcompanhamentos(response.data);
  };

  const formatarMoeda = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor);
  };

  const formatarData = (data: string) => {
    if (!data) return '-';
    return new Date(data).toLocaleDateString('pt-BR');
  };

  const handleImportExcel = async (file: File) => {
    try {
      setImporting(true);
      console.log('Iniciando importação do arquivo:', file.name);
      console.log('Tipo do arquivo:', file.type);
      console.log('Tamanho:', file.size);
      
      // Validar arquivo
      if (!file.name.match(/\.(xlsx|xls)$/)) {
        console.error('Arquivo não é Excel:', file.name);
        alert('Por favor, selecione um arquivo Excel (.xlsx ou .xls)');
        return;
      }
      
      const formData = new FormData();
      formData.append('file', file);
      
      console.log('FormData criado, verificando conteúdo...');
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      for (const [key, value] of formData.entries() as any) {
        console.log(`FormData ${key}:`, value);
      }
      
      console.log('Enviando requisição para:', '/api/etl/importar-excel-portuarios');
      
      const response = await api.post('/etl/importar-excel-portuarios', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('Resposta do servidor:', response.status);
      console.log('Dados da resposta:', response.data);
      
      if (response.status === 200) {
        alert('Planilha importada com sucesso!');
        setShowImportModal(false);
        carregarDados();
      } else {
        console.error('Status não esperado:', response.status);
        alert('Erro ao importar planilha. Status: ' + response.status);
      }
    } catch (error: any) {
      console.error('Erro completo na importação:', error);
      console.error('Response:', error.response);
      console.error('Mensagem:', error.message);
      
      if (error.response) {
        console.error('Status:', error.response.status);
        console.error('Data:', error.response.data);
        alert(`Erro ${error.response.status}: ${error.response.data.detail || error.response.data.message || 'Erro desconhecido'}`);
      } else {
        alert('Erro ao importar planilha. Verifique a conexão com o servidor.');
      }
    } finally {
      setImporting(false);
    }
  };

  const handleTest = () => {
    console.log('Botão clicado!');
    alert('Botão está funcionando!');
  };

  const renderizarTabelaConcessoes = () => (
    <div className="table-responsive">
      <table className="table table-striped table-hover">
        <thead className="table-dark">
          <tr>
            <th>Zona Portuária</th>
            <th>UF</th>
            <th>Obj. de Concessão</th>
            <th>Tipo</th>
            <th>CAPEX Total</th>
            <th>Data Assinatura</th>
            <th>Descrição</th>
            <th>Coord. E (UTM)</th>
            <th>Coord. S (UTM)</th>
            <th>Fuso</th>
          </tr>
        </thead>
        <tbody>
          {concessoes.map((concessao) => (
            <tr key={concessao.id}>
              <td>{concessao.zona_portuaria.nome}</td>
              <td>{concessao.zona_portuaria.uf}</td>
              <td>{concessao.objeto_concessao}</td>
              <td>
                <span className={`badge bg-${concessao.tipo === 'Concessão' ? 'primary' : concessao.tipo === 'Arrendamento' ? 'success' : 'info'}`}>
                  {concessao.tipo}
                </span>
              </td>
              <td>{formatarMoeda(concessao.capex_total)}</td>
              <td>{formatarData(concessao.data_assinatura)}</td>
              <td>{concessao.descricao || '-'}</td>
              <td>{concessao.coord_e || '-'}</td>
              <td>{concessao.coord_s || '-'}</td>
              <td>{concessao.fuso || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderizarTabelaServicos = () => (
    <div className="table-responsive">
      <table className="table table-striped table-hover">
        <thead className="table-dark">
          <tr>
            <th>Obj. de Concessão</th>
            <th>Tipo de Serviço</th>
            <th>Fase</th>
            <th>Serviço</th>
            <th>Descrição do Serviço</th>
            <th>Prazo Início (anos)</th>
            <th>Data Início</th>
            <th>Prazo Final (anos)</th>
            <th>Data Final</th>
            <th>Fonte (Prazo)</th>
            <th>% de CAPEX</th>
            <th>CAPEX do Serviço</th>
            <th>Fonte (% do CAPEX)</th>
          </tr>
        </thead>
        <tbody>
          {servicos.map((servico) => (
            <tr key={servico.id}>
              <td>{servico.concessao.objeto_concessao}</td>
              <td>
                <span className="badge bg-secondary">
                  {servico.tipo_servico.nome}
                </span>
              </td>
              <td>
                <span className="badge bg-warning text-dark">
                  {servico.fase}
                </span>
              </td>
              <td>{servico.nome}</td>
              <td>{servico.descricao || '-'}</td>
              <td>{servico.prazo_inicio_anos || '-'}</td>
              <td>{formatarData(servico.data_inicio)}</td>
              <td>{servico.prazo_final_anos || '-'}</td>
              <td>{formatarData(servico.data_final)}</td>
              <td>{servico.fonte_prazo || '-'}</td>
              <td>
                <div className="progress" style={{ width: '100px' }}>
                  <div 
                    className="progress-bar" 
                    role="progressbar" 
                    style={{ width: `${servico.percentual_capex}%` }}
                  >
                    {servico.percentual_capex}%
                  </div>
                </div>
              </td>
              <td>{formatarMoeda(servico.capex_servico)}</td>
              <td>{servico.fonte_percentual || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderizarTabelaAcompanhamentos = () => (
    <div className="table-responsive">
      <table className="table table-striped table-hover">
        <thead className="table-dark">
          <tr>
            <th>Serviço</th>
            <th>% Executada</th>
            <th>CAPEX (Reaj.)</th>
            <th>Valor Executado</th>
            <th>Data da Atualização</th>
            <th>Responsável</th>
            <th>Cargo</th>
            <th>Setor</th>
            <th>Riscos Relacionados</th>
          </tr>
        </thead>
        <tbody>
          {acompanhamentos.map((acompanhamento) => (
            <tr key={acompanhamento.id}>
              <td>
                <div>
                  <strong>{acompanhamento.servico.nome}</strong>
                  <br />
                  <small className="text-muted">
                    {acompanhamento.servico.concessao.objeto_concessao}
                  </small>
                </div>
              </td>
              <td>
                <div className="progress" style={{ width: '100px' }}>
                  <div 
                    className={`progress-bar ${acompanhamento.percentual_executado >= 80 ? 'bg-success' : acompanhamento.percentual_executado >= 50 ? 'bg-warning' : 'bg-danger'}`}
                    role="progressbar" 
                    style={{ width: `${acompanhamento.percentual_executado}%` }}
                  >
                    {acompanhamento.percentual_executado}%
                  </div>
                </div>
              </td>
              <td>{formatarMoeda(acompanhamento.capex_reajustado)}</td>
              <td>{formatarMoeda(acompanhamento.valor_executado)}</td>
              <td>{formatarData(acompanhamento.data_atualizacao)}</td>
              <td>{acompanhamento.responsavel}</td>
              <td>{acompanhamento.cargo}</td>
              <td>{acompanhamento.setor}</td>
              <td>
                {acompanhamento.riscos.map((risco, index) => (
                  <span key={index} className="badge bg-danger me-1">
                    {risco.tipo}
                  </span>
                ))}
                {acompanhamento.riscos.length === 0 && '-'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <div className="portos">
      <div className="container">
        <div className="hero">
          <h1>🚢 Sistema Portuário</h1>
          <p className="subtitle">
            Sistema completo para gestão de concessões portuárias, serviços e acompanhamentos.
          </p>
        </div>

        {/* Abas de navegação */}
        <ul className="nav nav-tabs" id="portosTab" role="tablist">
          <li className="nav-item" role="presentation">
            <button 
              className={`nav-link ${abaAtiva === 'concessoes' ? 'active' : ''}`}
              onClick={() => setAbaAtiva('concessoes')}
              type="button"
              role="tab"
              aria-controls="concessoes"
              aria-selected={abaAtiva === 'concessoes'}
            >
              Concessões
            </button>
          </li>
          <li className="nav-item" role="presentation">
            <button 
              className={`nav-link ${abaAtiva === 'servicos' ? 'active' : ''}`}
              onClick={() => setAbaAtiva('servicos')}
              type="button"
              role="tab"
              aria-controls="servicos"
              aria-selected={abaAtiva === 'servicos'}
            >
              Serviços
            </button>
          </li>
          <li className="nav-item" role="presentation">
            <button 
              className={`nav-link ${abaAtiva === 'acompanhamentos' ? 'active' : ''}`}
              onClick={() => setAbaAtiva('acompanhamentos')}
              type="button"
              role="tab"
              aria-controls="acompanhamentos"
              aria-selected={abaAtiva === 'acompanhamentos'}
            >
              Acompanhamentos
            </button>
          </li>
        </ul>

        {/* Botões de ação */}
        <div className="action-buttons">
          <div className="btn-group" role="group">
            <button 
              className="btn btn-success"
              onClick={() => {
                if (abaAtiva === 'concessoes') setShowConcessaoForm(true);
                else if (abaAtiva === 'servicos') setShowServicoForm(true);
                else setShowAcompanhamentoForm(true);
              }}
            >
              ➕ Novo {abaAtiva === 'concessoes' ? 'Cadastro' : abaAtiva === 'servicos' ? 'Serviço' : 'Acompanhamento'}
            </button>
            <button 
              className="btn btn-info"
              onClick={() => setShowImportModal(true)}
            >
              📥 Importar Excel
            </button>
            <button 
              className="btn btn-outline-secondary"
              onClick={handleTest}
            >
              🔄 Testar
            </button>
            <button 
              className="btn btn-outline-primary"
              onClick={carregarDados}
            >
              🔄 Atualizar
            </button>
          </div>
        </div>

      {carregando && (
        <div className="text-center my-5">
          <div className="loading-spinner"></div>
          <p className="mt-2">Carregando dados...</p>
        </div>
      )}

      {erro && (
        <div className="alert alert-danger" role="alert">
          <strong>Erro:</strong> {erro}
          <button className="btn btn-sm btn-danger ms-2" onClick={carregarDados}>
            Tentar novamente
          </button>
        </div>
      )}

      {!carregando && !erro && (
        <div className="card fade-in">
          <div className="card-header">
            <h5 className="mb-0">
              {abaAtiva === 'concessoes' && '📋 Concessões Portuárias'}
              {abaAtiva === 'servicos' && '🔧 Serviços Portuários'}
              {abaAtiva === 'acompanhamentos' && '📊 Acompanhamentos'}
            </h5>
          </div>
          <div className="card-body">
            {abaAtiva === 'concessoes' && concessoes.length === 0 && (
              <div className="empty-state">
                <h4>Nenhuma concessão cadastrada</h4>
                <p>Clique em "Novo Cadastro" para adicionar a primeira concessão.</p>
              </div>
            )}
            {abaAtiva === 'servicos' && servicos.length === 0 && (
              <div className="empty-state">
                <h4>Nenhum serviço cadastrado</h4>
                <p>Clique em "Novo Serviço" para adicionar o primeiro serviço.</p>
              </div>
            )}
            {abaAtiva === 'acompanhamentos' && acompanhamentos.length === 0 && (
              <div className="empty-state">
                <h4>Nenhum acompanhamento cadastrado</h4>
                <p>Clique em "Novo Acompanhamento" para adicionar o primeiro acompanhamento.</p>
              </div>
            )}
            
            {abaAtiva === 'concessoes' && concessoes.length > 0 && renderizarTabelaConcessoes()}
            {abaAtiva === 'servicos' && servicos.length > 0 && renderizarTabelaServicos()}
            {abaAtiva === 'acompanhamentos' && acompanhamentos.length > 0 && renderizarTabelaAcompanhamentos()}
          </div>
        </div>
      )}

      {/* Resumo */}
      <div className="summary-card">
        <div className="card-body">
          <h5 className="card-title mb-3">📈 Resumo</h5>
          <div className="row text-center">
            <div className="col">
              <h4 className="text-primary">{concessoes.length}</h4>
              <small>Concessões</small>
            </div>
            <div className="col">
              <h4 className="text-success">{servicos.length}</h4>
              <small>Serviços</small>
            </div>
            <div className="col">
              <h4 className="text-warning">{acompanhamentos.length}</h4>
              <small>Acompanhamentos</small>
            </div>
          </div>
        </div>
      </div>

      {/* Modal de Importação de Excel */}
      {showImportModal && (
        <div className="modal show" style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">📥 Importar Planilha Portuária</h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => setShowImportModal(false)}
                ></button>
              </div>
              <div className="modal-body">
                <div className="alert alert-info">
                  <h6>📋 Estrutura da Planilha Esperada:</h6>
                  <div className="row">
                    <div className="col-md-4">
                      <strong>Tabela 0 - Cadastro:</strong><br />
                      Zona portuária, UF, Obj. de Concessão, Tipo, CAPEX Total, Data de assinatura, Descrição, Coordenada E, Coordenada S, Fuso
                    </div>
                    <div className="col-md-4">
                      <strong>Tabela 1 - Serviços:</strong><br />
                      Obj. de Concessão, Tipo de Serviço, Fase, Serviço, Descrição, Prazos, % CAPEX, CAPEX do Serviço
                    </div>
                    <div className="col-md-4">
                      <strong>Tabela 2 - Acompanhamento:</strong><br />
                      Serviço, % executada, CAPEX (Reaj.), Valor executado, Data da atualização, Responsável, Cargo, Setor, Riscos
                    </div>
                  </div>
                </div>
                
                <div className="mb-3">
                  <label htmlFor="excelFile" className="form-label">Selecione a planilha Excel:</label>
                  <input 
                    type="file" 
                    className="form-control" 
                    id="excelFile"
                    accept=".xlsx,.xls"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        handleImportExcel(file);
                      }
                    }}
                  />
                  {importing && (
                    <div className="mt-2">
                      <div className="loading-spinner"></div>
                      <small className="text-muted">Importando planilha...</small>
                    </div>
                  )}
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setShowImportModal(false)}
                  disabled={importing}
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Cadastro de Concessão */}
      {showConcessaoForm && (
        <div className="modal show" style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">➕ Nova Concessão Portuária</h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => setShowConcessaoForm(false)}
                ></button>
              </div>
              <div className="modal-body">
                <form>
                  <div className="mb-3">
                    <label className="form-label">Zona Portuária</label>
                    <select className="form-select">
                      <option value="">Selecione...</option>
                      <option value="1">Porto Organizado de Santos</option>
                      <option value="2">Porto Organizado do Rio de Janeiro</option>
                      <option value="3">Porto Organizado de Maceió</option>
                      <option value="4">Porto Organizado de São Sebastião</option>
                      <option value="5">Não se aplica - MT/MS</option>
                      <option value="6">Não se aplica - PR</option>
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Objeto de Concessão</label>
                    <input type="text" className="form-control" placeholder="Ex: TECON 10" />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Tipo</label>
                    <select className="form-select">
                      <option value="">Selecione...</option>
                      <option value="Concessão">Concessão</option>
                      <option value="Arrendamento">Arrendamento</option>
                      <option value="Autorização">Autorização</option>
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">CAPEX Total</label>
                    <input type="number" className="form-control" placeholder="0.00" />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Data de Assinatura</label>
                    <input type="date" className="form-control" />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Descrição</label>
                    <textarea className="form-control" rows={3} placeholder="Descrição da concessão..."></textarea>
                  </div>
                  <div className="row">
                    <div className="col-md-6 mb-3">
                      <label className="form-label">Coordenada E (UTM)</label>
                      <input type="number" className="form-control" placeholder="0.00" />
                    </div>
                    <div className="col-md-6 mb-3">
                      <label className="form-label">Coordenada S (UTM)</label>
                      <input type="number" className="form-control" placeholder="0.00" />
                    </div>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Fuso</label>
                    <input type="number" className="form-control" placeholder="23" />
                  </div>
                </form>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setShowConcessaoForm(false)}
                >
                  Cancelar
                </button>
                <button type="button" className="btn btn-success">
                  Salvar Concessão
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Cadastro de Serviço */}
      {showServicoForm && (
        <div className="modal show" style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">➕ Novo Serviço Portuário</h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => setShowServicoForm(false)}
                ></button>
              </div>
              <div className="modal-body">
                <form>
                  <div className="mb-3">
                    <label className="form-label">Concessão</label>
                    <select className="form-select">
                      <option value="">Selecione...</option>
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Tipo de Serviço</label>
                    <select className="form-select">
                      <option value="">Selecione...</option>
                      <option value="1">CMO</option>
                      <option value="2">Disponibilidade de Infraestrutura</option>
                    </select>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Fase</label>
                    <input type="text" className="form-control" placeholder="Ex: 1ª" />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Nome do Serviço</label>
                    <input type="text" className="form-control" placeholder="Nome do serviço..." />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Descrição</label>
                    <textarea className="form-control" rows={3} placeholder="Descrição do serviço..."></textarea>
                  </div>
                  <div className="row">
                    <div className="col-md-6 mb-3">
                      <label className="form-label">% de CAPEX</label>
                      <input type="number" className="form-control" placeholder="0.00" min="0" max="100" />
                    </div>
                    <div className="col-md-6 mb-3">
                      <label className="form-label">CAPEX do Serviço</label>
                      <input type="number" className="form-control" placeholder="0.00" />
                    </div>
                  </div>
                </form>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setShowServicoForm(false)}
                >
                  Cancelar
                </button>
                <button type="button" className="btn btn-success">
                  Salvar Serviço
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Cadastro de Acompanhamento */}
      {showAcompanhamentoForm && (
        <div className="modal show" style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">➕ Novo Acompanhamento</h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => setShowAcompanhamentoForm(false)}
                ></button>
              </div>
              <div className="modal-body">
                <form>
                  <div className="mb-3">
                    <label className="form-label">Serviço</label>
                    <select className="form-select">
                      <option value="">Selecione...</option>
                    </select>
                  </div>
                  <div className="row">
                    <div className="col-md-6 mb-3">
                      <label className="form-label">% Executada</label>
                      <input type="number" className="form-control" placeholder="0.00" min="0" max="100" />
                    </div>
                    <div className="col-md-6 mb-3">
                      <label className="form-label">CAPEX (Reaj.)</label>
                      <input type="number" className="form-control" placeholder="0.00" />
                    </div>
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Valor Executado</label>
                    <input type="number" className="form-control" placeholder="0.00" />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Data da Atualização</label>
                    <input type="date" className="form-control" />
                  </div>
                  <div className="row">
                    <div className="col-md-4 mb-3">
                      <label className="form-label">Responsável</label>
                      <input type="text" className="form-control" placeholder="Nome do responsável" />
                    </div>
                    <div className="col-md-4 mb-3">
                      <label className="form-label">Cargo</label>
                      <input type="text" className="form-control" placeholder="Cargo" />
                    </div>
                    <div className="col-md-4 mb-3">
                      <label className="form-label">Setor</label>
                      <input type="text" className="form-control" placeholder="Setor" />
                    </div>
                  </div>
                </form>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setShowAcompanhamentoForm(false)}
                >
                  Cancelar
                </button>
                <button type="button" className="btn btn-success">
                  Salvar Acompanhamento
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  );
};

export default Portos;
