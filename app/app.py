from __future__ import annotations
import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

import services as svc
import io_utils as iox
import db

# Inicializar banco de dados
db.init_db()

st.set_page_config(page_title='Gestão de Concessões Portuárias', layout='wide')

# Sidebar para navegação
st.sidebar.title("🚢 Gestão Portuária")
st.sidebar.markdown("---")

# Navegação entre páginas
pagina = st.sidebar.selectbox(
    "Selecione a página:",
    ["📊 Dashboard", "📋 Planilha 00 - Cadastro", "📋 Planilha 01 - Serviços", "📋 Planilha 02 - Acompanhamento"]
)

# Função para mostrar detalhes do porto
def show_porto_details(porto_id):
    """Exibe detalhes completos de um porto específico com mapa"""
    
    try:
        conn = db.sqlite3.connect(db.DB_PATH)
        
        # Dados principais do porto
        query_porto = """
        SELECT 
            c.id,
            c.local as name,
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
            st.error(f"Porto não encontrado (ID: {porto_id})")
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
        st.subheader(f"📍 Ficha do Porto: {porto['name']}")
        
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
        
        # Mapa
        if pd.notna(porto['coord_e_utm']) and pd.notna(porto['coord_s_utm']):
            st.write("**🗺️ Localização:**")
            
            # Conversão UTM para lat/lng (aproximada para o Brasil)
            # Usando uma conversão simplificada para demonstração
            utm_e = float(porto['coord_e_utm'])
            utm_n = float(porto['coord_s_utm'])
            fuso = int(porto['fuso']) if pd.notna(porto['fuso']) else 23
            
            # Conversão aproximada (simplificada)
            # Para precisão real, seria necessário usar bibliotecas como pyproj
            # Esta é uma aproximação para o território brasileiro
            
            # Fórmula simplificada para conversão UTM -> lat/lng
            # Considerando o datum SIRGAS2000 (comum no Brasil)
            lat = -15.0 + (utm_n - 8300000) / 110000  # Aproximação para latitude
            lng = -60.0 + (utm_e - 500000) / 110000 + (fuso - 21) * 6  # Aproximação para longitude
            
            # Ajustes finos para melhor precisão
            lat = max(-33.75, min(5.27, lat))  # Limites do Brasil
            lng = max(-73.99, min(-28.85, lng))  # Limites do Brasil
            
            # Criar dados para o mapa
            map_data = pd.DataFrame({
                'lat': [lat],
                'lon': [lng],
                'name': [porto['name']],
                'description': [f"Coordenadas UTM: E={utm_e}, N={utm_n}, Fuso={fuso}<br>Lat/Lng: {lat:.4f}, {lng:.4f}"]
            })
            
            # Criar mapa com Plotly
            fig_map = px.scatter_mapbox(
                map_data,
                lat="lat",
                lon="lon", 
                hover_name="name",
                hover_data=["description"],
                zoom=8,
                height=400,
                mapbox_style="open-street-map",
                title=f"Localização - {porto['name']}"
            )
            
            fig_map.update_layout(
                margin={"r":0,"t":30,"l":0,"b":0}
            )
            
            st.plotly_chart(fig_map, use_container_width=True)
            
            # Informações de coordenadas
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"📍 **Coordenadas UTM:**<br>E: {utm_e}<br>N: {utm_n}<br>Fuso: {fuso}")
            with col2:
                st.info(f"🌍 **Coordenadas Geográficas:**<br>Latitude: {lat:.6f}°<br>Longitude: {lng:.6f}°")
            
            st.info("📍 **Nota:** Conversão UTM para lat/lng é aproximada. Para precisão cartográfica, seria necessária biblioteca especializada como pyproj.")
        else:
            st.warning("📍 Coordenadas não disponíveis para este porto.")
        
        if not df_servicos.empty:
            st.write("**🔧 Serviços:**")
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
            st.write("**📅 Atualizações Recentes:**")
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
            if 'selected_porto_id' in st.session_state:
                del st.session_state.selected_porto_id
            st.rerun()
            
    except Exception as e:
        st.error(f"Erro ao carregar detalhes do porto: {e}")

# Conteúdo principal baseado na página selecionada
if pagina == "📊 Dashboard":
    st.header("📊 Dashboard de Concessões Portuárias")
    
    # Carregar dados do banco
    try:
        conn = db.sqlite3.connect(db.DB_PATH)
        
        # Dados principais dos portos
        query_portos = """
        SELECT 
            c.id,
            c.local as name,
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
        ORDER BY c.local
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
        df_portos = pd.DataFrame()
    
    # Se não houver dados, mostrar mensagem
    if df_portos.empty:
        st.info("📝 Nenhum dado encontrado. Adicione portos através das abas 'Planilha 00', 'Planilha 01' e 'Planilha 02'.")
    else:
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label="📍 Total de Portos", value=total_portos)
        
        with col2:
            st.metric(
                label="💰 Investimento Total",
                value=f"R$ {total_investment/1000000:.1f}M" if total_investment > 0 else "R$ 0"
            )
        
        with col3:
            st.metric(label="📈 Progresso Médio", value=f"{avg_progress:.1f}%")
        
        with col4:
            st.metric(label="⚙️ Serviços Ativos", value=int(total_services))
        
        # Gráfico de status
        st.subheader("📊 Distribuição por Status")
        status_counts = df_portos['status'].value_counts()
        
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Distribuição por Status",
            color_discrete_map={
                'Concluído': '#2E7D32',
                'Em Andamento': '#2E4E8C',
                'Planejamento': '#F7B500'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de portos
        st.subheader("📋 Lista de Portos")
        
        # Preparar dados para exibição
        df_display = df_portos.copy()
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
        
        # Adicionar coluna de IDs para os botões
        df_display['ID'] = df_portos['id']  # Usar ID real do banco em vez do index
        
        # Mostrar tabela sem botões HTML
        st.dataframe(df_display, use_container_width=True)
        
        # Adicionar botões de detalhes separadamente
        st.subheader("🔍 Ações")
        if df_display.empty:
            st.warning("Nenhum porto encontrado para exibir ações.")
        else:
            cols = st.columns(min(4, len(df_display)))
            for i, (_, row) in enumerate(df_display.iterrows()):
                with cols[i % 4]:
                    if st.button(f"Ver Detalhes - {row['Porto']}", key=f"detalhes_{row['ID']}"):
                        st.session_state.selected_porto_id = row['ID']
                        st.rerun()
        
        # Verificar se foi solicitado detalhes de um porto específico
        if 'selected_porto_id' in st.session_state:
            show_porto_details(st.session_state.selected_porto_id)

elif pagina == "📋 Planilha 00 - Cadastro":
    st.title('Gestão de Concessões Portuárias – Planilha 00')
    
    # Carregar dados do banco na primeira execução
    if 'df00' not in st.session_state:
        st.session_state.df00, st.session_state.df01, st.session_state.df02 = db.load_all()
        if st.session_state.df00.empty and st.session_state.df01.empty and st.session_state.df02.empty:
            # Se não houver dados no banco, inicializar com DataFrames vazios
            st.session_state.df00 = pd.DataFrame(columns=iox.COLS_00)
            st.session_state.df01 = pd.DataFrame(columns=iox.COLS_01)
            st.session_state.df02 = pd.DataFrame(columns=iox.COLS_02)

    st.sidebar.header('Banco de Dados')
    if st.sidebar.button('💾 Salvar no banco de dados', use_container_width=True):
        if db.save_all(st.session_state.df00, st.session_state.df01, st.session_state.df02):
            st.sidebar.success('Dados salvos com sucesso!')
        else:
            st.sidebar.error('Erro ao salvar dados.')

    if st.sidebar.button('📥 Carregar do banco de dados', use_container_width=True):
        df00, df01, df02 = db.load_all()
        st.session_state.df00 = df00 if not df00.empty else pd.DataFrame(columns=iox.COLS_00)
        st.session_state.df01 = df01 if not df01.empty else pd.DataFrame(columns=iox.COLS_01)
        st.session_state.df02 = df02 if not df02.empty else pd.DataFrame(columns=iox.COLS_02)
        st.sidebar.success('Dados carregados com sucesso!')
        st.rerun()

    # Interface da Planilha 00
    st.subheader("Cadastro de Portos")
    edited_df = st.data_editor(st.session_state.df00, num_rows="dynamic", key="editor_00")
    st.session_state.df00 = edited_df

    # Botões de importação/exportação
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Importar Excel (todas as planilhas)", type=['xlsx'], key="upload_completo")
        if uploaded_file:
            try:
                df00, df01, df02 = iox.read_excel(uploaded_file)
                st.session_state.df00 = df00
                st.session_state.df01 = df01
                st.session_state.df02 = df02
                st.success(f"Arquivo importado com sucesso! {len(df00)} cadastros, {len(df01)} serviços, {len(df02)} acompanhamentos")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao importar arquivo: {e}")
        
        st.markdown("**Ou importar planilha individual:**")
        uploaded_file_00 = st.file_uploader("Planilha 00 apenas", type=['xlsx'], key="upload_00")
        if uploaded_file_00:
            df = pd.read_excel(uploaded_file_00)
            st.session_state.df00 = df
            st.success("Planilha 00 importada com sucesso!")
            st.rerun()

    with col2:
        if st.button("Exportar Excel (completo)"):
            output = BytesIO()
            iox.write_excel(output, st.session_state.df00, st.session_state.df01, st.session_state.df02)
            st.download_button(
                label="Baixar arquivo completo",
                data=output.getvalue(),
                file_name="portos_completo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

elif pagina == "📋 Planilha 01 - Serviços":
    st.title('Gestão de Concessões Portuárias – Planilha 01')
    
    # Carregar dados se necessário
    if 'df01' not in st.session_state:
        st.session_state.df00, st.session_state.df01, st.session_state.df02 = db.load_all()
        if st.session_state.df01.empty:
            st.session_state.df01 = pd.DataFrame(columns=iox.COLS_01)

    st.subheader("Serviços Portuários")
    edited_df = st.data_editor(st.session_state.df01, num_rows="dynamic", key="editor_01")
    st.session_state.df01 = edited_df

    # Botões de importação/exportação
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Importar Excel (todas as planilhas)", type=['xlsx'], key="upload_completo_01")
        if uploaded_file:
            try:
                df00, df01, df02 = iox.read_excel(uploaded_file)
                st.session_state.df00 = df00
                st.session_state.df01 = df01
                st.session_state.df02 = df02
                st.success(f"Arquivo importado com sucesso! {len(df00)} cadastros, {len(df01)} serviços, {len(df02)} acompanhamentos")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao importar arquivo: {e}")
        
        st.markdown("**Ou importar planilha individual:**")
        uploaded_file_01 = st.file_uploader("Planilha 01 apenas", type=['xlsx'], key="upload_01")
        if uploaded_file_01:
            df = pd.read_excel(uploaded_file_01)
            st.session_state.df01 = df
            st.success("Planilha 01 importada com sucesso!")
            st.rerun()

    with col2:
        if st.button("Exportar Excel (completo)"):
            output = BytesIO()
            iox.write_excel(output, st.session_state.df00, st.session_state.df01, st.session_state.df02)
            st.download_button(
                label="Baixar arquivo completo",
                data=output.getvalue(),
                file_name="portos_completo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

elif pagina == "📋 Planilha 02 - Acompanhamento":
    st.title('Gestão de Concessões Portuárias – Planilha 02')
    
    # Carregar dados se necessário
    if 'df02' not in st.session_state:
        st.session_state.df00, st.session_state.df01, st.session_state.df02 = db.load_all()
        if st.session_state.df02.empty:
            st.session_state.df02 = pd.DataFrame(columns=iox.COLS_02)

    st.subheader("Acompanhamento de Obras")
    edited_df = st.data_editor(st.session_state.df02, num_rows="dynamic", key="editor_02")
    st.session_state.df02 = edited_df

    # Botões de importação/exportação
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Importar Excel (todas as planilhas)", type=['xlsx'], key="upload_completo_02")
        if uploaded_file:
            try:
                df00, df01, df02 = iox.read_excel(uploaded_file)
                st.session_state.df00 = df00
                st.session_state.df01 = df01
                st.session_state.df02 = df02
                st.success(f"Arquivo importado com sucesso! {len(df00)} cadastros, {len(df01)} serviços, {len(df02)} acompanhamentos")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao importar arquivo: {e}")
        
        st.markdown("**Ou importar planilha individual:**")
        uploaded_file_02 = st.file_uploader("Planilha 02 apenas", type=['xlsx'], key="upload_02")
        if uploaded_file_02:
            df = pd.read_excel(uploaded_file_02)
            st.session_state.df02 = df
            st.success("Planilha 02 importada com sucesso!")
            st.rerun()

    with col2:
        if st.button("Exportar Excel (completo)"):
            output = BytesIO()
            iox.write_excel(output, st.session_state.df00, st.session_state.df01, st.session_state.df02)
            st.download_button(
                label="Baixar arquivo completo",
                data=output.getvalue(),
                file_name="portos_completo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# Rodapé
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ Informações")
st.sidebar.info("""
- **Dashboard:** Visualização dos dados
- **Planilha 00:** Cadastro de portos
- **Planilha 01:** Serviços portuários  
- **Planilha 02:** Acompanhamento de obras

Os dados são salvos automaticamente no banco SQLite.
""")
