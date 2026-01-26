from __future__ import annotations
import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px

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
        st.dataframe(df_display, use_container_width=True)
    
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
