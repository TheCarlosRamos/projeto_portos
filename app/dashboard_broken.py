from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import db

def show_dashboard():
    """Exibe o dashboard de portos com dados do banco"""
    
    st.header("📊 Dashboard de Concessões Portuárias")
    
    # Carregar dados do banco
    try:
        conn = db.sqlite3.connect(db.DB_PATH)
        
        # Dados principais dos portos
        query_portos = """
        SELECT 
            c.id,
            c.zona_portuaria as name,
            c.obj_concessao as description,
            c.tipo as project_type,
            c.capex_total as investment,
            c.data_ass_contrato as contract_date,
            c.descricao as full_description,
            GROUP_CONCAT(DISTINCT uf.sigla) as ufs,
            COUNT(DISTINCT s.id) as total_services,
            COUNT(DISTINCT a.id) as total_updates,
            COALESCE(MAX(a.perc_executada), 0) as progress_percentage,
            CASE 
                WHEN MAX(a.perc_executada) >= 0.9 THEN 'Concluído'
                WHEN MAX(a.perc_executada) > 0 THEN 'Em Andamento'
                ELSE 'Planejamento'
            END as status
        FROM cadastro c
        LEFT JOIN cadastro_uf cu ON c.id = cu.cadastro_id
        LEFT JOIN uf uf ON cu.uf_sigla = uf.sigla
        LEFT JOIN servico s ON c.id = s.cadastro_id
        LEFT JOIN acompanhamento a ON s.id = a.servico_id
        GROUP BY c.id
        ORDER BY c.zona_portuaria
        """
        
        df_portos = pd.read_sql_query(query_portos, conn)
        
        # Dados resumidos
        total_portos = len(df_portos)
        total_investment = df_portos['investment'].fillna(0).sum()
        avg_progress = (df_portos['progress_percentage'].fillna(0) * 100).mean()
        total_services = df_portos['total_services'].fillna(0).sum()
        
        conn.close()
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return
    
    # Se não houver dados, mostrar mensagem
    if df_portos.empty:
        st.info("📝 Nenhum dado encontrado. Adicione portos através das abas 'Planilha 00', 'Planilha 01' e 'Planilha 02'.")
        return
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📍 Total de Portos",
            value=total_portos
        )
    
    with col2:
        st.metric(
            label="💰 Investimento Total",
            value=f"R$ {total_investment/1000000:.1f}M" if total_investment > 0 else "R$ 0"
        )
    
    with col3:
        st.metric(
            label="📈 Progresso Médio",
            value=f"{avg_progress:.1f}%"
        )
    
    with col4:
        st.metric(
            label="⚙️ Serviços Ativos",
            value=int(total_services)
        )
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de status
        status_counts = df_portos['status'].value_counts()
        
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Distribuição por Status",
            color_discrete_map={
                'Concluído': '#2E7D32',
                'Em Andamento': '#2E4E8C',
                'Planejamento': '#F7B500'
            }
        )
        fig_status.update_layout(height=300)
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Gráfico de progresso
        fig_progress = px.histogram(
            df_portos,
            x='progress_percentage',
            nbins=10,
            title="Distribuição de Progresso",
            labels={'progress_percentage': 'Progresso (%)', 'count': 'Número de Portos'},
            color_discrete_sequence=['#2E4E8C']
        )
        fig_progress.update_layout(height=300)
        st.plotly_chart(fig_progress, use_container_width=True)
    
    # Filtros
    st.subheader("🔍 Filtros")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Status",
            ["Todos"] + list(df_portos['status'].unique()),
            key="status_filter"
        )
    
    with col2:
        uf_filter = st.selectbox(
            "UF",
            ["Todos"] + sorted(set([uf for ufs in df_portos['ufs'].fillna('') for uf in ufs.split(',') if uf])),
            key="uf_filter"
        )
    
    with col3:
        search_term = st.text_input("🔍 Buscar porto", key="search_porto")
    
    # Aplicar filtros
    df_filtered = df_portos.copy()
    
    if status_filter != "Todos":
        df_filtered = df_filtered[df_filtered['status'] == status_filter]
    
    if uf_filter != "Todos":
        df_filtered = df_filtered[df_filtered['ufs'].str.contains(uf_filter, na=False)]
    
    if search_term:
        df_filtered = df_filtered[
            df_filtered['name'].str.contains(search_term, case=False, na=False) |
            df_filtered['description'].str.contains(search_term, case=False, na=False)
        ]
    
    # Cards dos portos
    st.subheader(f"📋 Portos ({len(df_filtered)} encontrados)")
    
    if df_filtered.empty:
        st.warning("Nenhum porto encontrado com os filtros selecionados.")
        return
    
    # Grid de cards
    cols = st.columns(3)
    
    for idx, (_, porto) in enumerate(df_filtered.iterrows()):
        with cols[idx % 3]:
            # Card HTML
            progress = porto['progress_percentage'] * 100
            investment = porto['investment'] if pd.notna(porto['investment']) else 0
            
            # Definir cor do status
            status_colors = {
                'Concluído': '#2E7D32',
                'Em Andamento': '#2E4E8C',
                'Planejamento': '#F7B500'
            }
            status_color = status_colors.get(porto['status'], '#6B7280')
            
            # HTML do card
            porto_id = porto['id']
            card_html = f"""
            <div style="
                background: white;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                border-left: 4px solid {status_color};
            ">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                    <h4 style="margin: 0; color: #1f2937; font-size: 16px;">{porto['name']}</h4>
                    <span style="
                        background: {status_color};
                        color: white;
                        padding: 4px 8px;
                        border-radius: 12px;
                        font-size: 12px;
                    ">{porto['status']}</span>
                </div>
                
                <p style="margin: 0 0 12px 0; color: #6b7280; font-size: 14px; line-height: 1.4;">
                    {porto['description'][:100]}{'...' if len(str(porto['description'])) > 100 else ''}
                </p>
                
                <div style="margin-bottom: 8px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span style="color: #6b7280; font-size: 12px;">Progresso</span>
                        <span style="color: #1f2937; font-size: 12px; font-weight: 600;">{progress:.1f}%</span>
                    </div>
                    <div style="
                        background: #e5e7eb;
                        border-radius: 9999px;
                        height: 8px;
                        overflow: hidden;
                    ">
                        <div style="
                            background: linear-gradient(90deg, #10b981, #059669);
                            height: 100%;
                            width: {progress}%;
                            transition: width 0.3s ease;
                        "></div>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px;">
                    <div>
                        <span style="color: #6b7280;">Investimento:</span>
                        <span style="color: #1f2937; font-weight: 600;">
                            {'R$ ' + f'{investment/1000000:.1f}M' if investment > 0 else 'N/A'}
                        </span>
                    </div>
                    <div>
                        <span style="color: #6b7280;">UFs:</span>
                        <span style="color: #1f2937; font-weight: 600;">{porto['ufs'] or 'N/A'}</span>
                    </div>
                    <div>
                        <span style="color: #6b7280;">Serviços:</span>
                        <span style="color: #1f2937; font-weight: 600;">{int(porto['total_services'])}</span>
                    </div>
                    <div>
                        <span style="color: #6b7280;">Tipo:</span>
                        <span style="color: #1f2937; font-weight: 600;">{porto['project_type'] or 'N/A'}</span>
                    </div>
                </div>
                
                <div style="margin-top: 12px;">
                    <button onclick="alert('Detalhes do porto {porto_id}')" style="background: {status_color}; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-size: 12px; cursor: pointer; width: 100%;">Ver Detalhes</button>
                </div>
            </div>
            """
            
            st.markdown(card_html, unsafe_allow_html=True)
    
    # Tabela detalhada
    with st.expander("📊 Tabela Detalhada"):
        # Preparar dados para exibição
        df_display = df_filtered.copy()
        df_display['progress_percentage'] = (df_display['progress_percentage'] * 100).round(1)
        df_display['investment'] = df_display['investment'].apply(
            lambda x: f"R$ {x/1000000:.1f}M" if pd.notna(x) and x > 0 else "N/A"
        )
        
        # Renomear colunas
        column_mapping = {
            'name': 'Porto',
            'description': 'Descrição',
            'status': 'Status',
            'progress_percentage': 'Progresso (%)',
            'investment': 'Investimento',
            'ufs': 'UFs',
            'total_services': 'Serviços',
            'project_type': 'Tipo'
        }
        
        df_display = df_display[list(column_mapping.keys())].rename(columns=column_mapping)
        st.dataframe(df_display, use_container_width=True)
    
    # Detalhes do porto selecionado
    if st.session_state.get('selected_porto_id'):
        show_porto_details(st.session_state.selected_porto_id)

def show_porto_details(porto_id):
    """Exibe detalhes completos de um porto específico"""
    
    try:
        conn = db.sqlite3.connect(db.DB_PATH)
        
        # Dados principais do porto
        query_porto = """
        SELECT 
            c.id,
            c.zona_portuaria as name,
            c.obj_concessao as description,
            c.tipo as project_type,
            c.capex_total as investment,
            c.data_ass_contrato as contract_date,
            c.descricao as full_description,
            c.coord_e_utm,
            c.coord_s_utm,
            c.fuso
        FROM cadastro c
        WHERE c.id = ?
        """
        
        porto = pd.read_sql_query(query_porto, conn, params=(porto_id,))
        
        if porto.empty:
            st.error("Porto não encontrado")
            conn.close()
            return
        
        porto = porto.iloc[0]
        
        # UFs do porto
        query_ufs = """
        SELECT uf.sigla FROM uf uf
        JOIN cadastro_uf cu ON uf.sigla = cu.uf_sigla
        WHERE cu.cadastro_id = ?
        """
        
        df_ufs = pd.read_sql_query(query_ufs, conn, params=(porto_id,))
        ufs = df_ufs['sigla'].tolist()
        
        # Serviços do porto
        query_servicos = """
        SELECT 
            s.id,
            s.tipo_servico,
            s.fase,
            s.servico,
            s.descricao_servico,
            s.prazo_inicio_anos,
            s.data_inicio,
            s.prazo_final_anos,
            s.data_final,
            s.fonte_prazo,
            s.perc_capex,
            s.capex_servico,
            s.fonte_perc_capex
        FROM servico s
        WHERE s.cadastro_id = ?
        ORDER BY s.tipo_servico, s.fase
        """
        
        df_servicos = pd.read_sql_query(query_servicos, conn, params=(porto_id,))
        
        # Acompanhamentos mais recentes
        query_acompanhamentos = """
        SELECT 
            a.descricao,
            a.perc_executada,
            a.capex_reaj,
            a.valor_executado,
            a.data_atualizacao,
            a.responsavel,
            a.cargo,
            a.setor,
            a.risco_tipo,
            a.risco_descricao
        FROM acompanhamento a
        JOIN servico s ON a.servico_id = s.id
        WHERE s.cadastro_id = ?
        ORDER BY a.data_atualizacao DESC
        LIMIT 10
        """
        
        df_acompanhamentos = pd.read_sql_query(query_acompanhamentos, conn, params=(porto_id,))
        
        conn.close()
        
        # Exibir detalhes
        st.markdown("---")
        st.subheader(f"📍 Detalhes do Porto: {porto['name']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Informações Gerais:**")
            st.write(f"- **Descrição:** {porto['description']}")
            st.write(f"- **Tipo:** {porto['project_type'] or 'N/A'}")
            st.write(f"- **Data do Contrato:** {porto['contract_date'] or 'N/A'}")
            st.write(f"- **Investimento:** R$ {porto['investment']/1000000:.1f}M" if pd.notna(porto['investment']) else "- **Investimento:** N/A")
            st.write(f"- **UFs:** {', '.join(ufs) if ufs else 'N/A'}")
        
        with col2:
            st.write("**Coordenadas:**")
            if pd.notna(porto['coord_e_utm']) and pd.notna(porto['coord_s_utm']):
                st.write(f"- **UTM E:** {porto['coord_e_utm']}")
                st.write(f"- **UTM N:** {porto['coord_s_utm']}")
                st.write(f"- **Fuso:** {porto['fuso'] or 'N/A'}")
            else:
                st.write("- Coordenadas não disponíveis")
        
        if pd.notna(porto['full_description']):
            st.write("**Descrição Completa:**")
            st.write(porto['full_description'])
        
        if not df_servicos.empty:
            st.write("**Serviços:**")
            for _, servico in df_servicos.iterrows():
                with st.expander(f"🔧 {servico['servico'] or 'Serviço sem nome'}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"- **Tipo:** {servico['tipo_servico'] or 'N/A'}")
                        st.write(f"- **Fase:** {servico['fase'] or 'N/A'}")
                        st.write(f"- **Início:** {servico['data_inicio'] or 'N/A'}")
                        st.write(f"- **Final:** {servico['data_final'] or 'N/A'}")
                    
                    with col2:
                        st.write(f"- **CAPEX:** R$ {servico['capex_servico']/1000000:.1f}M" if pd.notna(servico['capex_servico']) else "- **CAPEX:** N/A")
                        st.write(f"- **% CAPEX:** {servico['perc_capex']*100:.1f}%" if pd.notna(servico['perc_capex']) else "- **% CAPEX:** N/A")
                        st.write(f"- **Fonte Prazo:** {servico['fonte_prazo'] or 'N/A'}")
                    
                    if pd.notna(servico['descricao_servico']):
                        st.write("**Descrição:**")
                        st.write(servico['descricao_servico'])
        
        if not df_acompanhamentos.empty:
            st.write("**Atualizações Recentes:**")
            for _, acomp in df_acompanhamentos.iterrows():
                with st.expander(f"📅 {acomp['data_atualizacao']} - {acomp['responsavel'] or 'N/A'}"):
                    st.write(acomp['descricao'])
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if pd.notna(acomp['perc_executada']):
                            st.write(f"- **Executado:** {acomp['perc_executada']*100:.1f}%")
                        if pd.notna(acomp['valor_executado']):
                            st.write(f"- **Valor Executado:** R$ {acomp['valor_executado']/1000000:.1f}M")
                    
                    with col2:
                        st.write(f"- **Responsável:** {acomp['responsavel'] or 'N/A'}")
                        st.write(f"- **Cargo:** {acomp['cargo'] or 'N/A'}")
                        st.write(f"- **Setor:** {acomp['setor'] or 'N/A'}")
                    
                    with col3:
                        if pd.notna(acomp['risco_descricao']):
                            st.warning(f"⚠️ **Risco:** {acomp['risco_descricao']}")
        
        if st.button("🔙 Voltar para o Dashboard"):
            st.session_state.selected_porto_id = None
            st.rerun()
            
    except Exception as e:
        st.error(f"Erro ao carregar detalhes do porto: {e}")
