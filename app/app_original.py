from __future__ import annotations
import streamlit as st
import pandas as pd
from io import BytesIO

import services as svc
import io_utils as iox
import db
import dashboard

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
    dashboard.show_dashboard()
    
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
        uploaded_file = st.file_uploader("Importar Excel (Planilha 00)", type=['xlsx'], key="upload_00")
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            st.session_state.df00 = df
            st.success("Arquivo importado com sucesso!")
            st.rerun()

    with col2:
        if st.button("Exportar Excel (Planilha 00)"):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                st.session_state.df00.to_excel(writer, index=False, sheet_name='Cadastro')
            st.download_button(
                label="Baixar arquivo",
                data=output.getvalue(),
                file_name="planilha_00_cadastro.xlsx",
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
        uploaded_file = st.file_uploader("Importar Excel (Planilha 01)", type=['xlsx'], key="upload_01")
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            st.session_state.df01 = df
            st.success("Arquivo importado com sucesso!")
            st.rerun()

    with col2:
        if st.button("Exportar Excel (Planilha 01)"):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                st.session_state.df01.to_excel(writer, index=False, sheet_name='Serviços')
            st.download_button(
                label="Baixar arquivo",
                data=output.getvalue(),
                file_name="planilha_01_servicos.xlsx",
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
        uploaded_file = st.file_uploader("Importar Excel (Planilha 02)", type=['xlsx'], key="upload_02")
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            st.session_state.df02 = df
            st.success("Arquivo importado com sucesso!")
            st.rerun()

    with col2:
        if st.button("Exportar Excel (Planilha 02)"):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                st.session_state.df02.to_excel(writer, index=False, sheet_name='Acompanhamento')
            st.download_button(
                label="Baixar arquivo",
                data=output.getvalue(),
                file_name="planilha_02_acompanhamento.xlsx",
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
        else:
            st.error('Erro ao salvar no banco de dados.')

with aba_srv:
    st.subheader('Tabela 01 - Serviços')

    with st.expander('Novo serviço (assistido)'):
        if st.session_state.df00.empty:
            st.info('Cadastre ao menos um objeto na Tabela 00 para vincular serviços.')
        else:
            cad_keys = st.session_state.df00[['Zona portuária','UF','Obj. de Concessão']].astype(str)
            cad_keys['key'] = cad_keys['Zona portuária']+' | '+cad_keys['UF']+' | '+cad_keys['Obj. de Concessão']
            key2row = {row['key']: (row['Zona portuária'], row['UF'], row['Obj. de Concessão']) for _, row in cad_keys.iterrows()}
            chosen = st.selectbox('Vincular ao cadastro', list(key2row.keys()))

            col1, col2, col3 = st.columns(3)
            tipo_srv = col1.text_input('Tipo de Serviço')
            fase = col2.text_input('Fase')
            serv = col3.text_input('Serviço')

            desc_srv = st.text_input('Descrição do serviço')
            col4, col5 = st.columns(2)
            prazo_i = col4.number_input('Prazo início (anos)', min_value=0, step=1)
            prazo_f = col5.number_input('Prazo final (anos)', min_value=0, step=1)

            col6, col7 = st.columns(2)
            fonte_prazo = col6.text_input('Fonte (Prazo)', value='Estimado')
            perc_capex = col7.number_input('% de CAPEX para o serviço', min_value=0.0, max_value=100.0, value=10.0, help='0–100. Será normalizado.')
            col8, col9 = st.columns(2)
            fonte_perc = col8.text_input('Fonte (% do CAPEX)', value='Estimado')

            if st.button('Adicionar serviço'):
                z, uf, obj = key2row[chosen]
                new = {c: None for c in iox.COLS_01}
                new.update({
                    'Zona portuária': z,
                    'UF': uf,
                    'Obj. de Concessão': obj,
                    'Tipo de Serviço': tipo_srv,
                    'Fase': fase,
                    'Serviço': serv,
                    'Descrição do serviço': desc_srv,
                    'Prazo início (anos)': int(prazo_i),
                    'Prazo final (anos)': int(prazo_f),
                    'Fonte (Prazo)': fonte_prazo,
                    '% de CAPEX para o serviço': perc_capex,
                    'Fonte (% do CAPEX)': fonte_perc,
                })
                row = pd.Series(new)
                row = svc.compute_service_fields(row, st.session_state.df00)
                st.session_state.df01 = pd.concat([st.session_state.df01, pd.DataFrame([row])], ignore_index=True)
                st.success('Serviço adicionado com sucesso.')
                # Salvar automaticamente no banco
                if db.save_servicos(st.session_state.df01):
                    st.info('✅ Dados salvos automaticamente no banco de dados.')

    edited01 = st.data_editor(
        st.session_state.df01,
        use_container_width=True,
        num_rows='dynamic',
        column_config={
            '% de CAPEX para o serviço': st.column_config.NumberColumn(format='%.4f', help='Pode ser 0–1 ou 0–100; o app normaliza.'),
            'CAPEX do Serviço': st.column_config.NumberColumn(format='%.2f', disabled=True),
            'Data de início': st.column_config.DateColumn(format='DD/MM/YYYY'),
            'Data final': st.column_config.DateColumn(format='DD/MM/YYYY'),
        },
        hide_index=True,
    )

    col_a, col_b, col_c = st.columns(3)
    if col_a.button('Recalcular datas e CAPEX (todas as linhas)'):
        df = edited01.copy()
        df = df.apply(lambda r: svc.compute_service_fields(r, st.session_state.df00), axis=1)
        st.session_state.df01 = df
        st.success('Recalculado.')
        # Salvar automaticamente
        if db.save_servicos(df):
            st.info('✅ Dados salvos automaticamente no banco de dados.')
    if col_b.button('Validar serviços'):
        errs = svc.validate_servicos(edited01, st.session_state.df00)
        if errs.empty:
            st.success('Serviços válidos.')
            st.session_state.df01 = edited01
            # Salvar automaticamente no banco após validação
            if db.save_servicos(edited01):
                st.info('✅ Dados salvos automaticamente no banco de dados.')
        else:
            st.error('Erros encontrados:')
            st.dataframe(errs, use_container_width=True)
    if col_c.button('💾 Salvar serviços no banco'):
        if db.save_servicos(edited01):
            st.success('Serviços salvos no banco de dados!')
            st.session_state.df01 = edited01
        else:
            st.error('Erro ao salvar no banco de dados.')

with aba_mon:
    st.subheader('Tabela 02 - Acompanhamento')

    edited02 = st.data_editor(
        st.session_state.df02,
        use_container_width=True,
        num_rows='dynamic',
        column_config={
            '% executada': st.column_config.NumberColumn(format='%.4f', help='Pode ser 0–1 ou 0–100; o app normaliza ao exportar.'),
            'CAPEX (Reaj.)': st.column_config.NumberColumn(format='%.2f'),
            'Valor executado': st.column_config.NumberColumn(format='%.2f'),
            'Data da atualização': st.column_config.DateColumn(format='DD/MM/YYYY'),
        },
        hide_index=True,
    )

    col_val_ac, col_save_ac = st.columns(2)
    if col_val_ac.button('Validar acompanhamento'):
        errs = svc.validate_acompanhamento(edited02, st.session_state.df01)
        if errs.empty:
            st.success('Acompanhamento válido.')
            st.session_state.df02 = edited02
            # Salvar automaticamente no banco após validação
            if db.save_acompanhamento(edited02):
                st.info('✅ Dados salvos automaticamente no banco de dados.')
        else:
            st.error('Erros encontrados:')
            st.dataframe(errs, use_container_width=True)
    
    if col_save_ac.button('💾 Salvar acompanhamento no banco'):
        if db.save_acompanhamento(edited02):
            st.success('Acompanhamento salvo no banco de dados!')
            st.session_state.df02 = edited02
        else:
            st.error('Erro ao salvar no banco de dados.')

with aba_exp:
    st.subheader('Exportar Excel')
    st.caption('O arquivo conterá as três abas no padrão: Tabela 00/01/02.')

    df01 = st.session_state.df01.copy()
    df01['% de CAPEX para o serviço'] = df01['% de CAPEX para o serviço'].apply(svc.normalize_percentage)

    df02 = st.session_state.df02.copy()
    df02['% executada'] = df02['% executada'].apply(svc.normalize_percentage)

    buffer = BytesIO()
    iox.write_excel(buffer, st.session_state.df00, df01, df02)
    buffer.seek(0)

    st.download_button('Baixar planilha .xlsx', data=buffer, file_name='portos_concessoes.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
