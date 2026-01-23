import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Processo {
  id: number;
  numero_processo: string;
  data_protocolo?: string;
  licenca?: string;
  situacao_geral_id?: number;
  situacao?: {
    id: number;
    nome: string;
  };
  metas?: Meta[];
  created_at?: string;
  updated_at?: string;
}

export interface Meta {
  id: number;
  processo_id: number;
  ano: number;
  indicadores?: Indicador[];
  created_at?: string;
  updated_at?: string;
}

export interface Indicador {
  id: number;
  meta_id: number;
  tipo_intervencao: string;
  financeiro_planejado: number;
  financeiro_executado: number;
  km_planejado: number;
  km_executado: number;
  extensao_km: number;
  created_at?: string;
  updated_at?: string;
}

export interface Situacao {
  id: number;
  nome: string;
  created_at?: string;
}

// Processos
export const processosApi = {
  listar: (params?: { skip?: number; limit?: number; numero_processo?: string; situacao_id?: number }) =>
    api.get<Processo[]>('/processos/', { params }),
  obter: (id: number) => api.get<Processo>(`/processos/${id}`),
  criar: (data: Partial<Processo>) => api.post<Processo>('/processos/', data),
  atualizar: (id: number, data: Partial<Processo>) =>
    api.put<Processo>(`/processos/${id}`, data),
  deletar: (id: number) => api.delete(`/processos/${id}`),
};

// Metas
export const metasApi = {
  listar: (params?: { skip?: number; limit?: number; ano?: number; processo_id?: number }) =>
    api.get<Meta[]>('/metas/', { params }),
  obter: (id: number) => api.get<Meta>(`/metas/${id}`),
  criar: (data: Partial<Meta>) => api.post<Meta>('/metas/', data),
  atualizar: (id: number, data: Partial<Meta>) =>
    api.put<Meta>(`/metas/${id}`, data),
  deletar: (id: number) => api.delete(`/metas/${id}`),
};

// Indicadores
export const indicadoresApi = {
  listar: (params?: { skip?: number; limit?: number; meta_id?: number; tipo_intervencao?: string }) =>
    api.get<Indicador[]>('/indicadores/', { params }),
  obter: (id: number) => api.get<Indicador>(`/indicadores/${id}`),
  criar: (data: Partial<Indicador>) => api.post<Indicador>('/indicadores/', data),
  atualizar: (id: number, data: Partial<Indicador>) =>
    api.put<Indicador>(`/indicadores/${id}`, data),
  deletar: (id: number) => api.delete(`/indicadores/${id}`),
};

// Situações
export const situacoesApi = {
  listar: () => api.get<Situacao[]>('/situacoes/'),
  obter: (id: number) => api.get<Situacao>(`/situacoes/${id}`),
  criar: (data: Partial<Situacao>) => api.post<Situacao>('/situacoes/', data),
  deletar: (id: number) => api.delete(`/situacoes/${id}`),
};

// ETL
export const etlApi = {
  importarExcel: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/etl/importar-excel', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  importarExcelPortuarios: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/etl/importar-excel-portuarios', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

// APIs Portuárias
export const portosApi = {
  // Concessões
  listarConcessoes: () => api.get('/concessoes/'),
  obterConcessao: (id: number) => api.get(`/concessoes/${id}`),
  criarConcessao: (data: any) => api.post('/concessoes/', data),
  atualizarConcessao: (id: number, data: any) => api.put(`/concessoes/${id}`, data),
  deletarConcessao: (id: number) => api.delete(`/concessoes/${id}`),
  
  // Serviços
  listarServicos: () => api.get('/servicos/'),
  obterServico: (id: number) => api.get(`/servicos/${id}`),
  criarServico: (data: any) => api.post('/servicos/', data),
  atualizarServico: (id: number, data: any) => api.put(`/servicos/${id}`, data),
  deletarServico: (id: number) => api.delete(`/servicos/${id}`),
  
  // Acompanhamentos
  listarAcompanhamentos: () => api.get('/acompanhamentos/'),
  obterAcompanhamento: (id: number) => api.get(`/acompanhamentos/${id}`),
  criarAcompanhamento: (data: any) => api.post('/acompanhamentos/', data),
  atualizarAcompanhamento: (id: number, data: any) => api.put(`/acompanhamentos/${id}`, data),
  deletarAcompanhamento: (id: number) => api.delete(`/acompanhamentos/${id}`),
  
  // Domínios
  listarZonasPortuarias: () => api.get('/dominios/zonas-portuarias/'),
  listarTiposServico: () => api.get('/dominios/tipos-servico/'),
  listarRiscos: () => api.get('/dominios/riscos/'),
};

export default api;
